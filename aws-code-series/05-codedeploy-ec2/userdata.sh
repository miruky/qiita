#!/bin/bash
yum update -y
yum install -y httpd ruby wget

# Apacheの起動
systemctl start httpd
systemctl enable httpd

# CodeDeploy Agentのインストール
cd /tmp
wget https://aws-codedeploy-ap-northeast-1.s3.ap-northeast-1.amazonaws.com/latest/install
chmod +x ./install
./install auto
systemctl start codedeploy-agent
systemctl enable codedeploy-agent
