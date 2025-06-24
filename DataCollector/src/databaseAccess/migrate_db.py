from database import Database

db = Database()



if __name__ == "__main__":
    db.migrate_old_entries_to_new_schema()
