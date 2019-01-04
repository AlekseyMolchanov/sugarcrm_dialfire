# Export SugarCRM tasks to DialFire.com


# Install

    Define Environment Variables

    DIALFIRE_CAMPAIGN_ID
    DIALFIRE_CAMPAIGN_TOKEN
    DIALFIRE_TASK_NAME

    SUGAR_CRM_URL
    SUGAR_CRM_USERNAME
    SUGAR_CRM_PASSWORD
    	
# Usage

    Just run 

    ./sync.py

# Install as periodic task

    add to cron (crontab -e)

    * * * * * cd <you folder> && ./sync.py

