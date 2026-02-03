import pymysql
import sys

pymysql.install_as_MySQLdb()
import MySQLdb
MySQLdb.version_info = (10, 0, 0, 'final', 0)
MySQLdb.__version__ = "10.0.0"
sys.modules['MySQLdb'] = MySQLdb
