# Agentic Support Copilot Workflow

This diagram shows the sequential flow of agents processing support requests.

---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	classify(classify)
	retrieve(retrieve)
	write(write)
	validate(validate)
	log(log)
	__end__([<p>__end__</p>]):::last
	__start__ --> classify;
	classify --> retrieve;
	log --> __end__;
	retrieve --> write;
	validate --> log;
	write --> validate;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc


## Agent Descriptions

1. **Classifier Agent**: Identifies intent, sentiment, and urgency
2. **Retriever Agent**: Fetches relevant knowledge from the database
3. **Writer Agent**: Generates a grounded response
4. **Guard Agent**: Validates safety and compliance
5. **Logger Agent**: Logs metrics and final evaluation
