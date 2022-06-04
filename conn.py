
#To read from database
def connection_database_read():

    import pymysql
    import paramiko
    import pandas as pd
    from paramiko import SSHClient
    from sshtunnel import SSHTunnelForwarder
    from os.path import expanduser


    mypkey = paramiko.RSAKey.from_private_key_file('new_key.pem')


    sql_hostname = '127.0.0.1'
    sql_username = 'root'
    sql_password = 'oxmTtOe5WyE8'
    sql_main_database = 'test'
    sql_port = 3306
    ssh_host = '3.25.164.2'
    ssh_user = 'bitnami'
    ssh_port = 22


    df_csv = pd.read_csv('MappingData.csv',header=0,index_col=0)






    with SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=mypkey,
            remote_bind_address=(sql_hostname, sql_port)) as tunnel:
        conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                 passwd=sql_password, db=sql_main_database,
                 port=tunnel.local_bind_port)


        #Write the query here
        query = '''SELECT * FROM 2019_results;'''
        #df_csv.to_sql('MappingData', conn, if_exists='append', index = False)
        data = pd.read_sql_query(query, conn)
        print(data)
        data.to_csv("2019_results_fromDB.csv")
        conn.close()


#Write to database function
def connection_database_write():

    import pymysql
    import paramiko
    import pandas as pd
    from paramiko import SSHClient
    from sshtunnel import SSHTunnelForwarder
    from os.path import expanduser


    #access key
    mypkey = paramiko.RSAKey.from_private_key_file('new_key.pem')


    sql_hostname = '127.0.0.1'
    sql_username = 'root'
    sql_password = 'oxmTtOe5WyE8'
    sql_main_database = 'test'
    sql_port = 3306
    ssh_host = '3.25.164.2'
    ssh_user = 'bitnami'
    ssh_port = 22


    df_csv = pd.read_csv('MappingData.csv')
    #df_csv = df_csv[:5]

    df = pd.DataFrame(df_csv)


    with SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=mypkey,
            remote_bind_address=(sql_hostname, sql_port)) as tunnel:
        conn = pymysql.connect(host='127.0.0.1', user=sql_username,
                               passwd=sql_password, db=sql_main_database,
                               port=tunnel.local_bind_port)
        cursor = conn.cursor()

        #drop table
        cursor.execute('DROP TABLE Test_push04')

        # Create Table
        cursor.execute('CREATE TABLE Test_push04 (BayID int(11),HOUR int(11), DOW int(11), Percent_Occupied float, lon float, lat float,Description text)')

        for row in df.itertuples():
            #print(row.BayID)
            a = row.BayID
            b = row.HOUR
            c= row.DOW
            d= row.Percent_Occupied
            e=row.lon
            f=row.lat
            g=row.Description
            cursor.execute('''
                        INSERT INTO Test_push04 (BayID ,HOUR, DOW, Percent_Occupied, lon, lat, Description)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        ''',
                        (a,b,c,d,e,f,g)


                           )

        conn.commit()







