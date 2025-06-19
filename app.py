import aws_cdk as cdk
from message_processing_stack import MessageProcessingStack

app = cdk.App()
MessageProcessingStack(app, "MessageProcessingStack")
app.synth()
