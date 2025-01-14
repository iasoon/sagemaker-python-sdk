# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""This module contains code to create and manage SageMaker ``LineageTrialComponent``."""
from __future__ import absolute_import

import logging

from typing import List

from sagemaker.apiutils import _base_types
from sagemaker.lineage.query import (
    LineageQuery,
    LineageFilter,
    LineageSourceEnum,
    LineageEntityEnum,
    LineageQueryDirectionEnum,
)
from sagemaker.lineage.artifact import Artifact


LOGGER = logging.getLogger("sagemaker")


class LineageTrialComponent(_base_types.Record):
    """An Amazon SageMaker, lineage trial component, which is part of a SageMaker lineage.

    A trial component is a stage in a trial.
    Trial components are created automatically within the SageMaker runtime and also can be
    created directly. To automatically associate trial components with a trial and experiment
    supply an experiment config when creating a job.
    For example: https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateTrainingJob.html

    Attributes:
        trial_component_name (str): The name of the trial component. Generated by SageMaker from the
            name of the source job with a suffix specific to the type of source job.
            trial_component_arn (str): The ARN of the trial component.
        display_name (str): The name of the trial component that will appear in UI,
            such as SageMaker Studio.
        source (obj): A TrialComponentSource object with a source_arn attribute.
        status (str): Status of the source job.
        start_time (datetime): When the source job started.
        end_time (datetime): When the source job ended.
        creation_time (datetime): When the source job was created.
        created_by (obj): Contextual info on which account created the trial component.
        last_modified_time (datetime): When the trial component was last modified.
        last_modified_by (obj): Contextual info on which account last modified the trial component.
        parameters (dict): Dictionary of parameters to the source job.
        input_artifacts (dict): Dictionary of input artifacts.
        output_artifacts (dict): Dictionary of output artifacts.
        metrics (obj): Aggregated metrics for the job.
        parameters_to_remove (list): The hyperparameters to remove from the component.
        input_artifacts_to_remove (list): The input artifacts to remove from the component.
        output_artifacts_to_remove (list): The output artifacts to remove from the component.
        tags (List[dict[str, str]]): A list of tags to associate with the trial component.
    """

    trial_component_name = None
    trial_component_arn = None
    display_name = None
    source = None
    status = None
    start_time = None
    end_time = None
    creation_time = None
    created_by = None
    last_modified_time = None
    last_modified_by = None
    parameters = None
    input_artifacts = None
    output_artifacts = None
    metrics = None
    parameters_to_remove = None
    input_artifacts_to_remove = None
    output_artifacts_to_remove = None
    tags = None

    _boto_create_method: str = "create_trial_component"
    _boto_load_method: str = "describe_trial_component"
    _boto_update_method: str = "update_trial_component"
    _boto_delete_method: str = "delete_trial_component"

    _boto_update_members = [
        "trial_component_name",
        "display_name",
        "status",
        "start_time",
        "end_time",
        "parameters",
        "input_artifacts",
        "output_artifacts",
        "parameters_to_remove",
        "input_artifacts_to_remove",
        "output_artifacts_to_remove",
    ]
    _boto_delete_members = ["trial_component_name"]

    @classmethod
    def load(cls, trial_component_name: str, sagemaker_session=None) -> "LineageTrialComponent":
        """Load an existing trial component and return an ``TrialComponent`` object representing it.

        Args:
            trial_component_name (str): Name of the trial component
            sagemaker_session (sagemaker.session.Session): Session object which
                manages interactions with Amazon SageMaker APIs and any other
                AWS services needed. If not specified, one is created using the
                default AWS configuration chain.
        Returns:
            LineageTrialComponent: A SageMaker ``LineageTrialComponent`` object
        """
        trial_component = cls._construct(
            cls._boto_load_method,
            trial_component_name=trial_component_name,
            sagemaker_session=sagemaker_session,
        )
        return trial_component

    def pipeline_execution_arn(self) -> str:
        """Get the ARN for the pipeline execution associated with this trial component (if any).

        Returns:
            str: A pipeline execution ARN.
        """
        tags = self.sagemaker_session.sagemaker_client.list_tags(
            ResourceArn=self.trial_component_arn
        )["Tags"]
        for tag in tags:
            if tag["Key"] == "sagemaker:pipeline-execution-arn":
                return tag["Value"]
        return None

    def dataset_artifacts(
        self, direction: LineageQueryDirectionEnum = LineageQueryDirectionEnum.ASCENDANTS
    ) -> List[Artifact]:
        """Use the lineage query to retrieve datasets that use this trial component.

        Args:
            direction (LineageQueryDirectionEnum, optional): The query direction.

        Returns:
            list of Artifacts: Artifacts representing a dataset.
        """
        query_filter = LineageFilter(
            entities=[LineageEntityEnum.ARTIFACT], sources=[LineageSourceEnum.DATASET]
        )
        query_result = LineageQuery(self.sagemaker_session).query(
            start_arns=[self.trial_component_arn],
            query_filter=query_filter,
            direction=direction,
            include_edges=False,
        )

        return [vertex.to_lineage_object() for vertex in query_result.vertices]

    def models(
        self, direction: LineageQueryDirectionEnum = LineageQueryDirectionEnum.DESCENDANTS
    ) -> List[Artifact]:
        """Use the lineage query to retrieve models that use this trial component.

        Args:
            direction (LineageQueryDirectionEnum, optional): The query direction.

        Returns:
            list of Artifacts: Artifacts representing a dataset.
        """
        query_filter = LineageFilter(
            entities=[LineageEntityEnum.ARTIFACT], sources=[LineageSourceEnum.MODEL]
        )
        query_result = LineageQuery(self.sagemaker_session).query(
            start_arns=[self.trial_component_arn],
            query_filter=query_filter,
            direction=direction,
            include_edges=False,
        )
        return [vertex.to_lineage_object() for vertex in query_result.vertices]
