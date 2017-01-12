import sqlite3

def new_db(dbpath):
    db = sqlite3.connect(dbpath)
    c = db.cursor()
    c.execute('''
        CREATE TABLE "Click" (
            `clickTime`	        text    not null 
                                        default current_timestamp,
            `buttonAlias`	integer not null,
            `delta`	        integer not null 
                                        default 1)
              ''')

    c.execute('''
        CREATE TABLE "ButtonAlias" (
	    `realButton`	integer not null,
	    `creationTime`	text not null default current_timestamp)
              ''')

    c.execute('''
        CREATE TABLE "Button" (
                `name`	                text not null unique,
                `initialValue`	        integer not null 
                                        default 0,
                `creationTime`	        text not null 
                                        default current_timestamp,
                `currentButtonAlias`	integer unique)
              ''')

    db.commit()

    return db

def load_db(dbpath):
    return sqlite3.connect(dbpath)

class Button():

    @staticmethod
    def new(db, name, initialValue=0):
        c = db.cursor()
        c.execute('''
            insert into Button (name, initialValue)
            values(?, ?)
        ''', (name, initialValue))

        b = Button(db, c.lastrowid)
        b.reset()
        return b


    @staticmethod
    def list(db): 
        c = db.cursor()
        c.execute('''
            select name, rowid from Button
        ''')

        return c.fetchall()

    @staticmethod
    def search(db, searchTerm): #TODO
        c = db.cursor()
        c.execute('''
            select name, rowid from Button
                where name like %?%
        ''', 
        (searchTerm, ))

        return c.fetchall()

    def __init__(self, db, id):
        self.db = db
        self.id = id

        self.c = self.db.cursor()
        self.retrieved = None

    @property
    def name(self):
        if not(self.retrieved):
            self.get()
        return self._name

    @property
    def initialValue(self):
        if not(self.retrieved):
            self.get()
        return self._initialValue

    @property
    def creationTime(self):
        if not(self.retrieved):
            self.get()
        return self._creationTime

    @property
    def lastReset(self):
        self.c.execute('''
            select ButtonAlias.creationTime from ButtonAlias
                inner join Button
                    on ButtonAlias.realButton = Button.rowid
            where ButtonAlias.rowid = Button.currentButtonAlias AND
                  Button.rowid = ?
                       ''', (self.id, ))

        return self.c.fetchone()[0]
       

    @property
    def alias(self):
        self.get()
        return self._currentButtonAlias
        
    @property
    def resets(self):
        self.c.execute('''
            select count(1) from ButtonAlias
                where ButtonAlias.realButton = ?
                       ''', (self.id, ))

        return self.c.fetchone()[0] - 1

    @property
    def clicks(self):
        self.c.execute('''
            select Click.delta
            from Button
                inner join ButtonAlias
                    on ButtonAlias.realButton = Button.rowid
                inner join Click
                    on ButtonAlias.rowid = Click.buttonAlias
            where Button.rowid = ? AND
                  ButtonAlias.rowid = Button.currentButtonAlias
                        ''', (self.id, ))

        currentTotal = sum(row[0] for row in self.c.fetchall())
        return currentTotal + self.initialValue

    def click(self, times=1):
        self.c.execute(''' 
            insert into Click (buttonAlias, delta) 
            values(?, ?)
                       ''', (self.alias, times))

        self.db.commit()

    def reset(self, times=1):
        self.c.execute(''' 
            insert into ButtonAlias (realButton) 
            values(?)
                       ''', (self.id, ))

        newButtonAliasID = self.c.lastrowid

        self.c.execute(''' 
           update Button
               set currentButtonAlias = ?
           where Button.rowid = ?
                      ''', (newButtonAliasID, self.id))

        self.db.commit()

    def get(self):
        self.c.execute('''
            select name,
                   initialValue,
                   creationTime,
                   currentButtonAlias
            from Button
                where Button.rowid = ?
                       ''', (self.id, ))

        row = self.c.fetchone()
        if row is not None:
            self._name               = row[0]
            self._initialValue       = row[1]
            self._creationTime       = row[2]
            self._currentButtonAlias = row[3]
        else:
            raise KeyError
