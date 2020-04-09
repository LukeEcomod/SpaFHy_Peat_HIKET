# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 15:02:38 2020

@author: 03110850
"""

import os
import boto3

if __name__ == '__main__':
    fdir='climate_data'
    os.makedirs(fdir, exist_ok=True)
    bucket='project_2000611-weather-climate'
    rcp=['rcp26','rcp45']

    s3 = boto3.client('s3', Bucket=bucket, endpoint_url='https://a3s.fi')

    for object in s3.list_objects()['Contents']:
        if len(object['Key'].split('.')) > 2:
            if object['Key'].split('.')[-2] in rcp:
                print(object['Key'])
                s3.download_file(bucket, object['Key'], os.path.join(fdir,object['Key']))
