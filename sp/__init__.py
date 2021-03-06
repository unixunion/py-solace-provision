import logging
import os
import sys
from pathlib import Path

from libksettings import KSettings

logger = logging.getLogger("pysolpro")

__version__ = "0.2.9"

example_config = """---
solace_config:
  ssl:
    verify_ssl: False
    cert: certs/cert.pem
    
  config:
    host: http://localhost:8080
    username: admin
    password: admin
  monitor:
    host: http://localhost:8080
    username: admin
    password: admin
  action:
    host: http://localhost:8080
    username: admin
    password: admin
  #proxy: http://localhost:5555

commands:
  config:
    api_path: /SEMP/v2/config
    module: solace_semp_config
    models: solace_semp_config.models
    api_class: AllApi
    config_class: Configuration
    client_class: ApiClient
  monitor:
    api_path: /SEMP/v2/monitor
    module: solace_semp_monitor
    models: solace_semp_monitor.models
    api_class: AllApi
    config_class: Configuration
    client_class: ApiClient
  action:
    api_path: /SEMP/v2/action
    module: solace_semp_action
    models: solace_semp_action.models
    api_class: AllApi
    config_class: Configuration
    client_class: ApiClient

# the file name is taken from a key in these object types
data_mappings:
  MsgVpnQueue: queueName
  MsgVpn: msgVpnName
  DmrCluster: dmrClusterName
  MsgVpnClientProfile: clientProfileName
  DomainCertAuthority: certAuthorityName
  CertAuthority: certAuthorityName
  CertAuthorityOcspTlsTrustedCommonName: ocspTlsTrustedCommonName
  ClientCertAuthority: certAuthorityName
  ClientCertAuthorityOcspTlsTrustedCommonName: ocspTlsTrustedCommonName
  DmrClusterLink: remoteNodeName
  DmrClusterLinkRemoteAddress: remoteAddress
  DmrClusterLinkTlsTrustedCommonName: tlsTrustedCommonName
  MsgVpnAclProfile: aclProfileName
  # hashfile will name the file by hashing the payload
  MsgVpnAclProfileClientConnectException: hashfile
  MsgVpnAclProfilePublishException: hashfile
  MsgVpnAclProfilePublishTopicException: hashfile
  MsgVpnAclProfileSubscribeException: hashfile
  MsgVpnAclProfileSubscribeTopicException: hashfile
  MsgVpnAclProfileSubscribeShareNameException: hashfile
  # procedurally generated, pending review
  MsgVpnAuthenticationOauthProvider: oauthProviderName
  MsgVpnAuthorizationGroup: authorizationGroupName
  MsgVpnBridge: bridgeName
  MsgVpnBridgeRemoteMsgVpn: bridgeName
  MsgVpnBridgeRemoteSubscription: hashfile
  MsgVpnBridgeTlsTrustedCommonName: tlsTrustedCommonName
  MsgVpnClientUsername: clientUsername
  MsgVpnDistributedCache: cacheName
  MsgVpnDistributedCacheCluster: clusterName
  MsgVpnDistributedCacheClusterGlobalCachingHomeCluster: clusterName
  MsgVpnDistributedCacheClusterGlobalCachingHomeClusterTopicPrefix: hashfile
  MsgVpnDistributedCacheClusterInstance: hashfile
  MsgVpnDistributedCacheClusterTopic: hashfile
  MsgVpnDmrBridge: hashfile
  MsgVpnJndiConnectionFactory: connectionFactoryName
  MsgVpnJndiQueue: queueName
  MsgVpnJndiTopic: hashfile
  MsgVpnMqttRetainCache: cacheName
  MsgVpnMqttSession: hashfile
  MsgVpnMqttSessionSubscription: hashfile
  MsgVpnQueueSubscription: hashfile
  MsgVpnQueueTemplate: queueTemplateName
  MsgVpnReplayLog: replayLogName
  MsgVpnReplicatedTopic: hashfile
  MsgVpnRestDeliveryPoint: restDeliveryPointName
  MsgVpnRestDeliveryPointQueueBinding: restDeliveryPointName
  MsgVpnRestDeliveryPointRestConsumer: restConsumerName
  MsgVpnRestDeliveryPointRestConsumerTlsTrustedCommonName: tlsTrustedCommonName
  MsgVpnSequencedTopic: hashfile
  MsgVpnTopicEndpoint: topicEndpointName
  MsgVpnTopicEndpointTemplate: topicEndpointTemplateName

# used for when running PySolPro server
SERVER:
  host: 127.0.0.1
  port: 65411
"""

try:
    Path("%s/.pysolpro" % Path.home()).mkdir(exist_ok=True)
except Exception as e:
    logger.error("unable to create dir ~/.pysolpro: %s" % e)
    pass

try:
    logger.debug("loading pysolpro settings...")
    settings = KSettings(config_filename="solace.yaml",
                         config_filename_envvar="PYSOLPRO_CONFIG",
                         PLUGINS=[],
                         config_load_locations=[os.getcwd(), "%s/.pysolpro" % Path.home(), "/", "/opt/pysolpro", "/etc/pysolpro"],
                         load_yaml=True)
except Exception as e:
    logger.error("Example Config:\n %s" % example_config)
    logger.error("Configuration not present, for more info, see https://github.com/unixunion/py-solace-provision")
    sys.exit(1)

solace_semp_unavailable_error = "\nUnable to import solace_semp_config, try:\n\n\tpip install " \
                                "solace_semp_config==SOLACE_VERSION\n\nSee " \
                                "https://pypi.org/project/solace-semp-config/#history for available versions\n\n "
