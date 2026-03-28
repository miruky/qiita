# policy/terraform.rego
# OPA (Open Policy Agent) ポリシー

package terraform

import input as tfplan

# 許可するインスタンスタイプ
allowed_instance_types := {"t3.micro", "t3.small", "t3.medium"}

# インスタンスタイプの制限
deny[msg] {
  resource := tfplan.resource_changes[_]
  resource.type == "aws_instance"
  resource.change.after.instance_type != null
  not resource.change.after.instance_type in allowed_instance_types
  msg := sprintf(
    "EC2 インスタンス '%s' のインスタンスタイプ '%s' は許可されていません。許可: %v",
    [resource.address, resource.change.after.instance_type, allowed_instance_types]
  )
}

# EBS 暗号化の強制
deny[msg] {
  resource := tfplan.resource_changes[_]
  resource.type == "aws_ebs_volume"
  resource.change.after.encrypted != true
  msg := sprintf(
    "EBS ボリューム '%s' は暗号化が有効になっていません",
    [resource.address]
  )
}
