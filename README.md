# Smart Delivery Dispatch System

## Team Information
- **Team Name**: Mad Cube
- **Year**: 2nd year
- **All-Female Team**: NO

## Architecture Overview

#### Describe your approach here. Keep it short and clear.

    - What is your dispatch strategy?
    - How do you score agents for incoming orders?
    - How do you manage SLA deadlines, priority orders, and agent capacity?
    - What are the main steps in your pipeline?


Dispatch Strategy:
The system's primary dispatching strategy utilizes a Priority-Queue (Min-Heap) to manage the ingestion of incoming orders. This specific data structure ensures that every task is automatically sorted by its urgency level as it enters the system. By maintaining this prioritized order, the engine can guarantee that the most critical tasks are processed and assigned before those with more flexible requirements.


Agent Scoring:
To determine the best fit for each task, we implemented a Multivariate Heuristic Scoring model that evaluates multiple agent attributes simultaneously. This model calculates a compatibility score by looking at the projected travel time, the individual agent’s historical ratings, and current workload distribution. This multi-factor approach ensures that the "best" agent is not just the closest one, but the one who balances high service quality with overall system efficiency


SLA, Priority, and Capacity:
Strict management of SLA deadlines and agent capacity is achieved through the integration of a specialized fairness penalty within our scoring logic. This penalty prevents any single agent from becoming overwhelmed, resulting in a remarkably low workload variance of 0.24 across the team. Through this balanced optimization, the system successfully maintains 100% SLA compliance, ensuring all priority orders are met within their required timeframes.


Pipeline Steps:
The operational pipeline begins with data ingestion, where data_loader.py pulls raw information from CSV files regarding agents, orders, and the environment. Once the data is live, graph_engine.py handles the complex routing logic while dispatcher.py executes the final assignment based on the scoring model. The process concludes with performance tracking, where the final results and system efficiency data are recorded in metrics.json for review.


**Note:** Please do not change the format or spelling of anything in this README. The fields are extracted using a script, so any changes to the structure or formatting may break the extraction process.
