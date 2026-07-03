Run docker tag securekube-api:v1.1 $REGISTRY/$REPOSITORY:$IMAGE_TAG
The push refers to repository [12345.dkr.ecr.ap-southeast-1.amazonaws.com/securekube-api]
03fe984d94ff: Preparing
b4063f825032: Preparing
5c8add69b87b: Preparing
b2f286273a4b: Preparing
61f6bd04c618: Preparing
7f996e324bdc: Preparing
9bda7f9f691e: Preparing
ea513af48424: Preparing
3edb2192497a: Preparing
7f996e324bdc: Waiting
9bda7f9f691e: Waiting
ea513af48424: Waiting
3edb2192497a: Waiting
denied: User: arn:aws:sts::12345:assumed-role/securekube-github-actions-role/GitHubActions is not authorized to perform: ecr:InitiateLayerUpload on resource: arn:aws:ecr:ap-southeast-1:12345:repository/securekube-api because no identity-based policy allows the ecr:InitiateLayerUpload action
Error: Process completed with exit code 1.