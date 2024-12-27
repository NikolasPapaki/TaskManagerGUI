import oracledb
import re
from tkinter import messagebox
from Logging import Logger

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
        self.logger = Logger()

    def connect(self, username, password=None, host=None, port=None, service_name=None, sysdba=False, use_oracle_client=False) -> str:
        # Already connected to a db
        try:
            # If we are already connected then disconnect
            if self.connected:
                self.disconnect()

            if use_oracle_client:
                oracledb.init_oracle_client()
                self.conn = oracledb.connect(mode=oracledb.SYSDBA)
                self.logger.info("Connected locally using oracle client")
            else:
                self.conn = oracledb.connect(user=username, password=password,
                                dsn=f'{host}:{port}/{service_name}',
                                mode = oracledb.SYSDBA if sysdba else oracledb.DEFAULT_AUTH)

                self.logger.info(f"Connected to {service_name}")

            self.connected = True
            return None
        except oracledb.InterfaceError as e:
            self.logger.error(f"Error while connecting to oracle database. {str(e)}")
            print("interface: " + str(e))
        except oracledb.DatabaseError as e:
            if "ORA-01017" in str(e):
                self.logger.error(f"Invalid credentials while connecting to oracle database. {str(e)}")
                return self.INVALID_PASS

            self.logger.error(f"Error while connecting to oracle database. {str(e)}")
            return str(e)

    def disconnect(self):
        try:
            if self.conn:
                self.logger.info(f"Disconnecting from {self.conn.dsn}")
                self.conn.close()
                self.connected = False
                self.logger.info(f"Disconnected")
        except oracledb.InterfaceError as e:
            # Already not connected so just set self.connected to False in case it was True
            if "DPY-1001" in str(e):
                self.connected = False
            else:
                self.logger.warning(f"Error while disconnecting from database. {str(e)}")
                messagebox.showwarning("Error", f"Error while disconnecting from database. {str(e)}")
        except oracledb.DatabaseError as e:
            self.logger.warning(f"Error while disconnecting from database. {str(e)}")
            messagebox.showwarning("Error", f"Error!. {str(e)}")

    def execute(self, plsql_block):
        result = []

        if self.connected and plsql_block:
            try:
                self.conn.ping()

                self.cur = self.conn.cursor()

                self.cur.callproc("DBMS_OUTPUT.ENABLE")

                rows = self.cur.execute(plsql_block)

                if rows:
                    for row in rows:
                        result.append(row)

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
                self.logger.warning(f"Error while executing code. {str(e)}")
                messagebox.showwarning("Warning", f"Error: {e}")
        else:
            self.logger.warning("Trying to execute code without being connected to a database")
            messagebox.showwarning("Warning", "Not connected to a database!")
        return result


    def parse_dsn(self, dsn):
        try:
            parts = dsn.split("/")
            host_port = parts[0]
            service_name = parts[1] if len(parts) > 1 else None

            host, port = host_port.split(":")

            return {
                "host": host,
                "port": port,
                "service": service_name
                }
        except Exception as e:
            self.logger.error(f"Error while parsing dsn!. {dsn}")
