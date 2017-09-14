#!/usr/bin/python
from datetime import datetime, timedelta
import boto3
import json
from pandas.io.json import json_normalize
import pandas as pd
from threading import Thread

'''
    Collect Max, Min, Average of CPU & DiskOps of instances from Cloudwatch. Get instance list from db for which data to be collected
    Use python multithreading to improve performance
'''

class cloudwatch():
    def __init__(self,region):
        self.client=boto3.client('cloudwatch',region)
        self.df=pd.DataFrame()
        self.end = datetime.utcnow()
        self.start = self.end - timedelta(days=1)
        self.row=[]

    def getmondata(self,instance_id,metric):
        try:
            results = self.client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName=metric,
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=self.start,
                EndTime=self.end,
                Period=300,
                Statistics=['Average'])
            df=json_normalize(results['Datapoints'])
            df['instance_id'] = instance_id
            #print df.head()
            df=df['Average'].groupby([df['instance_id']]).agg(['min','max','mean','count'])
            df=df.round(2)
            df.reset_index(inplace=True)
            df.fillna(0,inplace=True)
            for i in df.values:
                instance_id=i[0]
                min=str(i[1])
                max=str(i[2])
                avg=str(i[3])
                count=str(i[4])
                self.row.append((instance_id,metric,min,max,avg,count,self.end))
        except Exception as e:
           print("Caught exception : " + str(e))
           return 0

    def insertdata(self):
        #print self.row
        cursor.executemany("""INSERT INTO [[table name]] (instance_id,metric,min,max,avg,count,enddate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", self.row)
        conn.commit()
        cursor.close()
        conn.close()

def main():
    metrics=['CPUUtilization','DiskReadOps'] ## add metrics
    region="" ## provide aws region name
    sql="select instance_id from [[instance table ]] where region="+region
    cursor=[[execute sql]]
    numrows = int(cursor.rowcount)
    if numrows<1:
       print "Not enough instances"
       sys.exit(0)
    clw=cloudwatch(region)
    jobs=[]
    from range(0,numrows):
       row = cursor.fetchone()
       instance_id=row[0]
       for metric in metrics:
           print "Metric {}".format(metric)
           clw.getmondata(instance_id,metric)
           p = Thread(target=clw.getmondata, args=(instance_id,metric,))
           jobs.append(p)
           p.start()
    for j in jobs:
        j.join()
    clw.insertdata()

if __name__ == "__main__":
    main()
