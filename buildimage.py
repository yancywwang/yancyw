#!/usr/bin/env python3

import os
import subprocess
import argparse
import sys
import datetime
import logging


def create_dockerfile():
    dockerfile_content = f"""
FROM mirror.ccs.tencentyun.com/library/centos:latest
USER root
RUN echo "$AK"=AKIDHOJ0127A0f91jGgyRkvHTaFk8KJ43ueq
ENV PWD="postgresql://1.1.1.1:xxx@yyy"
ENV RSYNC_PASSWORD="TPcloud@123"
RUN echo "root:123456" | chpasswd
COPY virus .
"""

    # 写入 Dockerfile
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)

    return "Dockerfile"


def build_docker_image(image_name="tcss_cicd", tag=1, build_context="."):
    """
    构建 Docker 镜像
    """
    if tag is None:
        # 使用提交ID和时间戳作为标签
        commit_id = os.getenv("CI_COMMIT_SHA", "latest")[:8]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        tag = f"{timestamp}-{commit_id}"

    full_image_name = f"{image_name}:{tag}"

    # 执行 docker build 命令
    try:
        subprocess.run(
            ["docker", "build", "-t", full_image_name, build_context]
        )

        return full_image_name, 0

    except subprocess.CalledProcessError as e:
        return None, e.returncode


def push_docker_image(image_name, registry_url="139.199.178.171:8089/cicd"):
    if registry_url:
        # 添加仓库前缀
        remote_image = f"{registry_url}/{image_name}"
        subprocess.run(["docker", "tag", image_name, remote_image], check=True)
        image_to_push = remote_image
    else:
        image_to_push = image_name

    try:
        subprocess.run(
            ["docker", "push", image_to_push]
        )

        return image_to_push, 0

    except subprocess.CalledProcessError as e:
        return None, e.returncode


def main():
    # 创建 Dockerfile
    dockerfile_path = create_dockerfile()

    # 构建镜像
    image_name, build_status = build_docker_image()

    # 推送镜像
    push_docker_image(image_name=image_name)


if __name__ == "__main__":
    sys.exit(main())


