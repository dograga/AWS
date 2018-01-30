#!/usr/bin/python
import boto3
from datetime import datetime
from datetime import timedelta
from bson import json_util
import json


class awsec2inventory():
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

     def updateec2json(self,inst,resid):
         output={}
         output['ReservationId']=resid
         #print inst
         output["AccountId"]=self.acctid
         output['Platform']=self.instancekey(inst,'Platform')
         output['PublicIpAddress']=self.instancekey(inst,'PublicIpAddress')
         output['InstanceType']=self.instancekey(inst,'InstanceType')
         output['AvailabilityZone']=self.instancekey(inst,'AvailabilityZone')
         output['ImageId']=self.instancekey(inst,'ImageId')
         output['Monitoring']=inst['Monitoring']['State']
         output['PrivateIpAddress']=inst['PrivateIpAddress']
         output['State']=inst['State']['Name']
         output['LaunchTime']=inst['LaunchTime']
         output['VpcId']=inst['VpcId']
         output['InstanceId']=inst['InstanceId']
         try:
             output['tag']=[tag['Value'] for tag in inst['Tags']]
         except:
             output['tag']=""
         secgroups=""
         if output['State'] =='running':
             securityGroups = inst['SecurityGroups']
             secgroups = [secgroups['GroupName'] for secgroups in securityGroups]
             output['SecurityGroups']=secgroups
         self.inventory.append(output)


     def getinstanceinfo(self):
         for region in self.regions:
             ec = boto3.client('ec2',region)
             ecinventory    = ec.describe_instances()
             reservations = ecinventory.get('Reservations',[])
             for reservation in reservations:
                 resid = reservation['ReservationId']
                 instances=[i for i in reservation['Instances']]
                 for inst in instances:
                    try:
                        self.updateec2json(inst,resid)
                    except Exception as e:
                        print "Failed to update info "+str(e.args)+e.message

         inventory=json.loads(json.dumps(self.inventory,default=json_util.default))
         for i in inventory:
              print "============================"
              print(i)

a=awsec2inventory()
a.getinstanceinfo()
