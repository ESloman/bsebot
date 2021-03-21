import functools

from typing import Union

import boto3
from boto3.resources.base import ServiceResource


class AWSAPI(object):
    """

    """
    def __init__(self):
        """

        """
        pass

    @staticmethod
    def get_instance(instance_ids: Union[str, list]) -> Union[ServiceResource, list]:
        """

        :param instance_ids:
        :return:
        """

        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids, ]

        ec2_resource = boto3.resource("ec2")

        # this code is like this because I had grand dreams of making it a coroutine
        part = functools.partial(list, ec2_resource.instances.filter(InstanceIds=instance_ids))
        instances = part()

        if len(instance_ids) == 1 and len(instances) == 1:
            return instances[0]

        return instances

    def get_instance_state(self, instance_id: str) -> str:
        """

        :param instance_id:
        :return:
        """
        return self.get_instance(instance_id).state["Name"]

    def start_instance(self, instance_id: str) -> Union[None, dict]:
        """

        :param instance_id:
        :return:
        """
        instance = self.get_instance(instance_id)

        if instance.state["Code"] != 80:
            return
        else:
            return instance.start()

    def stop_instance(self, instance_id: str) -> Union[None, dict]:
        """

        :param instance_id:
        :return:
        """
        instance = self.get_instance(instance_id)

        if instance.state["Code"] != 16:
            return
        else:
            return instance.stop()
