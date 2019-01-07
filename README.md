# Export SugarCRM tasks to DialFire.com

[![CircleCI](https://circleci.com/gh/AlekseyMolchanov/sugarcrm_dialfire.svg?style=svg)](https://circleci.com/gh/AlekseyMolchanov/sugarcrm_dialfire)
[![codecov](https://codecov.io/gh/AlekseyMolchanov/sugarcrm_dialfire/branch/master/graph/badge.svg)](https://codecov.io/gh/AlekseyMolchanov/sugarcrm_dialfire)


# Install

Define Environment Variables

    DIALFIRE_CAMPAIGN_ID
    DIALFIRE_CAMPAIGN_TOKEN
    DIALFIRE_TASK_NAME

    SUGAR_CRM_URL
    SUGAR_CRM_USERNAME
    SUGAR_CRM_PASSWORD

Install requirements
    
    pip install -r requirements.txt
    	
# Usage

Just run 

    ./sync.py

    or run and read help
    
    ./sync.py --help

# Install as periodic task

    add to cron (crontab -e)

    * * * * * cd <you folder> && ./sync.py

