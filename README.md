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


Our dispatch strategy utilizes a Priority-Queue (Min-Heap) for order ingestion, ensuring that urgent tasks are processed and assigned before lower-priority requests. To match these orders with the best available personnel, we use a Multivariate Heuristic Scoring model that calculates a compatibility score by balancing travel time, agent ratings, and workload fairness. We manage SLA deadlines and priority orders through this scoring logic, specifically by introducing a fairness penalty that maintains a low workload variance ($0.24$) and achieves $100\%$ SLA compliance even when handling high-capacity demands. The main steps in our pipeline involve loading data from CSV files (agents, orders, and environment edges) via data_loader.py, processing these through the graph_engine.py for routing, and executing the final assignment logic in dispatcher.py to output performance results in metrics.json.  



**Note:** Please do not change the format or spelling of anything in this README. The fields are extracted using a script, so any changes to the structure or formatting may break the extraction process.
