#!/usr/bin/python
import boto3
from datetime import datetime
from bson import json_util
import json


class awsrdsinventory():
     def __init__(self):
         self.regions=["us-east-1"]
         self.inventory=[]
         self.acctid=boto3.client('sts').get_caller_identity().get('Account')

     def instancekey(self,inst,key):
         ## Module to handle potential unassigned value
         try:
             val=inst[key]
         except:
             val=""
         return val


     def updatedbjson(self,dbinstance):
           #print dbinstance
           output={}
           output["AccountId"]=self.acctid
           output["PubliclyAccessible"]=dbinstance["PubliclyAccessible"]
           output["MasterUsername"]=dbinstance["MasterUsername"]
           output["MonitoringInterval"]=dbinstance["MonitoringInterval"]
           output["LicenseModel"]=dbinstance["LicenseModel"]
           output["InstanceCreateTime"]=dbinstance["InstanceCreateTime"]
           output["AutoMinorVersionUpgrade"] =dbinstance["AutoMinorVersionUpgrade"]
           output["PreferredBackupWindow"] =dbinstance["PreferredBackupWindow"]
           output["AllocatedStorage"]=dbinstance["AllocatedStorage"]
           output["DBInstanceArn"]=dbinstance["DBInstanceArn"]
           output["BackupRetentionPeriod"] =dbinstance["BackupRetentionPeriod"]
           output['DBName']=self.instancekey(dbinstance,'DBName')
           output["PreferredMaintenanceWindow"]=dbinstance["PreferredMaintenanceWindow"]
           output['Port']=dbinstance['Endpoint']['Port']
           output['Address']=dbinstance['Endpoint']['Address']
           output["DBInstanceStatus"]=dbinstance["DBInstanceStatus"]
           output["IAMDatabaseAuthenticationEnabled"] =dbinstance["IAMDatabaseAuthenticationEnabled"]
           output["AvailabilityZone"]=dbinstance["AvailabilityZone"]
           output["StorageEncrypted"]=dbinstance["StorageEncrypted"]
           output["DBInstanceClass"]=dbinstance["DBInstanceClass"]
           output["DbInstancePort"]=dbinstance["DbInstancePort"]
           output["DBInstanceIdentifier"]=dbinstance["DBInstanceIdentifier"]
           self.inventory.append(output)


     def getinstanceinfo(self):
         for region in self.regions:
             rds = boto3.client('rds',region)
             rds    = rds.describe_db_instances()
             dbinstances=rds['DBInstances']
             for dbinstance in dbinstances:
                  #print dbinstance
                try:
                    self.updatedbjson(dbinstance)
                except Exception as e:
                    print "Failed to update info "+str(e.args)+e.message
         inventory=json.loads(json.dumps(self.inventory,default=json_util.default))
         for i in inventory:
              print "============================"
              print(i)


r=awsrdsinventory()
r.getinstanceinfo()
