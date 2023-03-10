import platform
import os
import sqlite3
import sys
from sqlite3.dbapi2 import Connection, Cursor

SYSTEM: str = platform.system().lower()
HOME: str = os.path.expanduser('~')
DEFAULT_DB_PATH: str = f'{HOME}{os.sep}.java_version_manager{os.sep}'
DEFAULT_FILENAME: str = 'main.db'
DEFAULT_TABLE_NAME: str = 'jdks'


def set_version(jdk_path: str) -> None:
    cmd: str = ''
    if SYSTEM in ['linux', 'darwin']:
        cmd = f'export JAVA_HOME={jdk_path}'

        if 'linux' == SYSTEM:
            with open(f'{HOME}/.bashrc', encoding='utf-8', mode='a') as file:
                file.write(cmd)
                print(
                    f'Command written to file succeed, '
                    f'please run command [source {HOME}/.bashrc] to complete settings.')

    elif SYSTEM in ['windows']:
        print(f'Changed JAVA_HOME to {jdk_path}')
        print(f"Running command: {cmd}")
        cmd = f'setx JAVA_HOME {jdk_path} /m'
        os.system(cmd)


if __name__ == '__main__':
    # For macOS users, there exist a binary for java management at /usr/libexec/java_home
    if 'darwin' == SYSTEM:
        print('You can use /usr/libexec/java_home as an alternative in a Mac, there is no need to use this '
              'program.')
        is_continue_use = input('Enter Y/y to continue or enter any other character to stop: ')
        if is_continue_use.lower() != 'y':
            exit(0)

    # Check whether the user is running this app at the first time
    first_run: bool = False
    if not os.path.exists(DEFAULT_DB_PATH):
        print(f'Path {DEFAULT_DB_PATH} does not exist, creating now.')
        os.makedirs(DEFAULT_DB_PATH)

    # Create SQLite Database connection
    db: Connection = sqlite3.connect(f'{DEFAULT_DB_PATH}{os.sep}{DEFAULT_FILENAME}')
    cursor: Cursor = db.cursor()

    # Check whether the table is existed
    tables = cursor.execute("select name from sqlite_master where type = 'table' order by name;") \
        .fetchall()
    # if table is not created, then create one
    if len(tables) == 0 or DEFAULT_TABLE_NAME not in tables[0]:
        first_run = True
        cursor.execute(f"""
create table {DEFAULT_TABLE_NAME}(
    version_code varchar(30) primary key,
    path text not null
)""")

    # Tell user not to delete db file
    if first_run:
        print(f"""Welcome to use java-version-manager!
We are giving you some important information about this program.

This application will write a file {DEFAULT_FILENAME} in [{DEFAULT_DB_PATH}], which is a unencrypted sqlite3 
database. This file contains important information about all installed jdks in your computer, so do not remove 
this file.""")

    # Detect system arguments
    if len(sys.argv) > 0:
        try:
            command = sys.argv[1]
            # Add jdk to db
            if command in ['-r', '--register']:
                version_code = sys.argv[2]
                path = sys.argv[3]

                sql_register_jdk = f"insert into jdks values (?, ?)"

                cursor.execute(sql_register_jdk, (version_code, path,))

                db.commit()
            elif command in ['-v', '--version']:
                version_code = sys.argv[2]

                sql_get_path = "select path from jdks where version_code = ?"

                data = cursor.execute(sql_get_path, (version_code,)).fetchone()
                if data is not None:
                    set_version(data[0])
                else:
                    print("Invalid jdk version code!")
            elif command in ['-h', '--help']:
                print("""This is a helpful tool to set JAVA_HOME in your system.

Usage:

    -r, --register <version_code> <jdk_path>
        Register a jdk to this util.
        Parameters:
            - version_code: a version code within 30 letters
            - jdk_path: your java home directory
        
    -v, --version <version_code>
        Change the JAVA_HOME to specified version.

    -h, --help
        Show this tip.""")
        except IndexError:
            print("""You can use -h or --help to see usage document.""")

    cursor.close()
