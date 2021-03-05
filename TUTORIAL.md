# Installing

    python -mvenv ~/spvenv
    source ~/spvenv/bin/activate
    pip install py-solace-provision
    pip install solace-semp-config==9.8.0.12

# Start a local broker

    docker-compose up -d
    
# Configure

Create solace.yaml 

    ---
    solace_config:
      ssl:
        verify_ssl: false
        cert: certs/cert.pem
      config:
        host: http://localhost:8080/SEMP/v2/config
        username: admin
        password: admin
    
    commands:
      config:
        module: solace_semp_config
        models: solace_semp_config.models
        api_class: AllApi
        config_class: Configuration
        client_class: ApiClient
    
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
      MsgVpnAclProfileClientConnectException: hashfile
      MsgVpnAclProfilePublishException: hashfile
      MsgVpnAclProfilePublishTopicException: hashfile
      MsgVpnAclProfileSubscribeException: hashfile
      MsgVpnAclProfileSubscribeTopicException: hashfile
      MsgVpnAclProfileSubscribeShareNameException: hashfile
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


# First Commands

Query the broker for the vpns

    pysolpro.py config get_msg_vpns

Create a queue

    pysolpro.py config create_msg_vpn_queue --body data/queue.yaml  --msg_vpn_name default

Lets shutdown the queue we just created

    pysolpro.py config update_msg_vpn_queue --body data/queue.yaml  --msg_vpn_name default --queue_name test --override egressEnabled false --override ingressEnabled false

# Use --override to provision many queues from template
    
    pysolpro.py config create_msg_vpn_queue --body data/queue.yaml  --msg_vpn_name default --override queueName test1
    pysolpro.py config create_msg_vpn_queue --body data/queue.yaml  --msg_vpn_name default --override queueName test2
    pysolpro.py config create_msg_vpn_queue --body data/queue.yaml  --msg_vpn_name default --override queueName test3   

# Query queues, filtering on enabled State

    pysolpro.py config get_msg_vpn_queues --msg_vpn_name default --where ingressEnabled==false

    pysolpro.py config get_msg_vpn_queues --msg_vpn_name default --where "queueName==test*"

# Let's save some objects to disk

    pysolpro.py --save --save-dir=output config get_msg_vpns
    pysolpro.py --save --save-dir=output config get_msg_vpn_queues --msg_vpn_name default

now review contents of `output/`

# Lets add a subscription onto queue `test`

We will read in a subscrioption yaml, target it onto a specific queue, and override a key in the file to indicate the same queue.

    pysolpro.py config create_msg_vpn_queue_subscription --body data/subscription.yaml --msg_vpn_name default --queue_name test --override queueName test

