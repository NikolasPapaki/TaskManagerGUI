import oracledb
import re
from tkinter import messagebox

class OracleDB:
    _instance = None  # Class-level variable to store the single instance
    INVALID_PASS = "Invalid-Password"
    ERROR = "Error"

    def __new__(cls, *args, **kwargs):
        """Override __new__ to ensure only one instance of Settings exists."""
        if not cls._instance:
            cls._instance = super(OracleDB, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.conn = None
        self.cur = None
        self.connected = False

    def connect(self, username, password, host, port, service_name) -> str:
        # Already connected to a db
        try:
            # If we are already connected then disconnect
            if self.connected:
                self.disconnect()

            self.conn = oracledb.connect(user=username, password=password,
                                dsn=f'{host}:{port}/{service_name}')
            self.connected = True
            return None
        except oracledb.InterfaceError as e:
            print("interface: " + str(e))
        except oracledb.DatabaseError as e:
            if "ORA-01017" in str(e):
                return self.INVALID_PASS

            return str(e)




    def disconnect(self):
        try:
            if self.conn:
                self.conn.close()
                self.connected = False
        except oracledb.InterfaceError as e:
            # Already not connected so just set self.connected to False in case it was True
            if "DPY-1001" in str(e):
                self.connected = False
            else:
                messagebox.showwarning("Error", f"Error while disconnecting from database. {str(e)}")
        except oracledb.DatabaseError as e:
            messagebox.showwarning("Error", f"Error!. {str(e)}")

    def execute(self, plsql_block):
        result = []

        if self.connected and plsql_block:
            try:
                self.conn.ping()

                self.cur = self.conn.cursor()

                self.cur.callproc("DBMS_OUTPUT.ENABLE")

                self.cur.execute(plsql_block)

                status = self.cur.var(int)
                while True:
                    line = self.cur.var(str)
                    self.cur.callproc("DBMS_OUTPUT.GET_LINE", (line, status))
                    if status.getvalue() != 0:
                        break
                    the_line = line.getvalue()
                    if the_line:
                        result.append(the_line)

                self.cur.close()
            except oracledb.DatabaseError as e:
                print("execute")
        else:
            messagebox.showwarning("Warning", "Not connected to a database!")
        return result


    def parse_dsn(self, dsn):
        parts = dsn.split("/")
        host_port = parts[0]
        service_name = parts[1] if len(parts) > 1 else None

        host, port = host_port.split(":")

        return {
            "host": host,
            "port": port,
            "service": service_name
            }

