from flask import Flask, jsonify
from ...settings import TVVConfigApi

#from tvvmiaapi import GraphQLView
#from graphql import graphql
#from TVVMiaAPI import tvvmiaapi

API_FORMAL_NAME = 'TVVMia'
API_NAME = 'tvvmiapi'
API_ROUTE_ROOT = '/' + API_NAME
API_ROUTE_ARMATURE_LIST = API_ROUTE_ROOT + '/armlist'
API_ROUTE__LIST = API_ROUTE_ROOT + '/'
API_ROUTE_ASSEMBLY_ROOT = API_ROUTE_ROOT + '/assemble'
API_ROUTE_ASSEMBLY_INITIATE = API_ROUTE_ASSEMBLY_ROOT + '/init/<blenderfile><midifile><instrumentname>'
API_ROUTE_ASSEMBLY_CANCEL = API_ROUTE_ASSEMBLY_ROOT + '/cancel/<id>'
API_ROUTE_ASSEMBLY_STATUS = API_ROUTE_ASSEMBLY_ROOT + '/status/<id>'

api = Flask(__name__)
config = TVVConfigApi()
api.debug(config.get(API_FORMAL_NAME, 'DEBUG'))

@api.route(API_ROUTE_ROOT)
def apiRoot():
    return {'Greetings': 'From ' + API_FORMAL_NAME}

@api.route(API_ROUTE_ARMATURE_LIST)
def apiArmatureList():
    TEST_ARM_1 = {'armature':'armature.name.001', 'object':'object.name.001'}
    TEST_ARM_2 = {'armature':'armature.name.002', 'object':'object.name.002'}
    TEST_ARM_3 = {'armature':'armature.name.003', 'object':'object.name.003'}
    TEST_ARM_LIST = [ TEST_ARM_1, TEST_ARM_2, TEST_ARM_3 ]
    return jsonify(TEST_ARM_LIST)

@api.route(API_ROUTE_ASSEMBLY_INITIATE)
def apiInitiate():
    TEST_ARM_1 = {'armature':'armature.name.001', 'object':'object.name.001'}
    TEST_ARM_2 = {'armature':'armature.name.002', 'object':'object.name.002'}
    TEST_ARM_3 = {'armature':'armature.name.003', 'object':'object.name.003'}
    TEST_ARM_LIST = [ TEST_ARM_1, TEST_ARM_2, TEST_ARM_3 ]
    return jsonify(TEST_ARM_LIST)

if __name__ == "__main__":
    api.run(debug=True)
