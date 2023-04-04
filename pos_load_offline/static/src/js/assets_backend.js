function remove_pos_database() {
    localStorage.clear();
    var database = this.odoo.session_info.db;
    for (var i = 0; i &lt; 100; i++) {
    IndexedDB.deleteDatabase(database + '_' + i);
    }
}
