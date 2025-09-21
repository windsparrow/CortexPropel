# CortexPropel

## What is CortexPropel?
CortexPropel is an intelligent project management agent product that helps you manage complex tasks more efficiently and intelligently.

## Why We Developed CortexPropel?
We aim to treat intelligence as a resource, leveraging accumulated intellectual resources to reduce cognitive load, lower the cost and difficulty of project/task management, and enhance the scientific nature of task/project management. This is reflected in:
- Providing exceptional intent understanding capabilities, eliminating the need to fill out numerous forms to manage complex tasks
- Offering PhD-level intelligence to help decompose, merge, and track tasks, while promptly identifying execution risks
- Delivering powerful task change management capabilities, automatically replanning optimal strategies after changes and batch-updating tasks

## Design Approach
1. **Automatic Modeling**: During project management initialization, automatically establish a scientific and reasonable **task management model**, including:
   - Task hierarchy model for layered, granular task management with both macro and micro perspectives
   - Constraint conditions
   - Resource dependencies
   - Project objectives, such as minimizing project completion time or reducing project costs

2. **Natural Language Task Entry/Update**: Users communicate tasks and progress to CortexPropel in natural language, and CortexPropel automatically records tasks and updates progress according to the task management model.

3. **Structured Thinking for Task Relationships and Project Risks**:
   - **Induction**: Summarize which progress items belong to the same task
   - **Deduction**: Deduce what subtasks are needed under a particular task
   - **Reasoning**: Infer the series of related changes and risks that modifications might trigger

4. **Dynamic Execution and Optimization**:
   - **Execution**: Insert new tasks, update existing task progress, and update project progress based on the task management model
   - **Optimization**: Scientifically analyze changes, plan optimal post-change strategies, and record them when necessary

5. **Support for Various Chart Displays**: Various charts include:
   - Project progress charts
   - Task dependency charts
   - Risk charts
   - Resource allocation charts
   - Other statistical charts and trend graphs

## Project Plan (Preliminary)

### Overall Plan
- **Phase 1**: Implement the agent to effectively manage one person's tasks
- **Phase 2**: Optimize the agent to manage sandbox simulation projects, such as "The Phoenix Project"
- **Phase 3**: Develop a highly intelligent agent capable of managing real, complex projects
- **Phase 4**: Support simultaneous management of multiple complex projects

### Phase 1 Plan

**Objective**: Effectively manage one person's tasks, such as personal health plans.
**Specific Work Items**:
- [ ] Establish task management data model
- [ ] Implement task entry/update functionality
- [ ] Implement task execution checking functionality
- [ ] Implement task scheduling functionality
- [ ] Support various chart display functionality

## Technical Architecture

**Agent Framework**: LangGraph
**Database**: Initially using file read/write operations
**Interface**: Initially using CLI interaction

## Some Reflections
> Agents are merely the means to achieve our goals, not the ends themselves. We will use agents to tap into the unlimited intellectual resources from LLMs.

> We believe in “brute intelligence” the way others believe in brute force.

> We believe that AI-era software can evolve autonomously.