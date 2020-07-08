# AWS-AccessKeys-Checker

This AWS Clouformation template creates an IAM user access keys aging checker system :)

The intention with this system is to make sure every IAM user has *only* 1 active access key and this access key can't be older than 90 days.

This is kind of useful for audits and to maintain a standard with all IAM users.

- The following variables must be modified:

ADMIN@EXAMPLE.COM 

<SNS_TOPIC>

ADMIN@EXAMPLE.COM = this would be the admin email that is going to receive notifications about every user.
For the <SNS_TOPIC> you could provide an ARN for an existing SNS topic or you could create it using this same template.

- There a reference for a "Layer" in the template for the lambda functions for the "boto3" module. It was created at the time this template was created, it *might* not be needed now.
