# Daily Goals for {{name}}

Date: {{date.strftime("%A %B %d, %Y")}}

## Daily Goals

_What are you working on today, as stated in today's standup?_

- [ ] TBD

## Task List

_Tasks from here are translated into work items or issues at the end of the day._

{% if date.strftime('%A') == 'Monday' %}
## Weekly Goals

_What are items that might be relevant to your Connect?_

- One

{% endif %}

{% if date.strftime('%A') == 'Friday' %}
## Weekly Summary

_What are items that might be relevant to your Connect?_

- One

{% endif %}

<!-->Daily Schedule v3.0</!-->