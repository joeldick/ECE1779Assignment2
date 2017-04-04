from __future__ import print_function  # Python 2/3 compatibility
import boto3


from flask import render_template, url_for, redirect, request
from app import app

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


@app.route('/create_table')
def create_table():
    table = dynamodb.create_table(
        TableName='Movies',
        KeySchema=[
            {
                'AttributeName': 'year',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'title',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'year',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'title',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    return redirect(url_for('index'))


@app.route('/delete_table')
def delete_table():

    response = dynamodb.delete_table(
        TableName='Movies'
    )

    return redirect(url_for('index'))

