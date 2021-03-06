import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import glob

def getCrumbHeader(jenkinsUrl, jenkinsUser, JenkinsToken):
    # Purpose: create and return crumb header required to trigger remote jenkins build.
    print 'Building crumb header'
    crumb_issue_url = "{}/crumbIssuer/api/json".format(jenkinsUrl)
    try:
        crumb_response = requests.get(crumb_issue_url, auth=(jenkinsUser, JenkinsToken),verify=False)
        crumb_dict = crumb_response.json()
        #print("Crumb response: {}".format(crumb_dict))

        # Extract the crumb field name and crumb value from response
        crumb_field = crumb_dict["crumbRequestField"]
        crumb_value = crumb_dict["crumb"]
        #print(("Field ID: {}{}".format(crumb_field, "\n") + "Crumb: {}".format(crumb_value)))
    except Exception as e:
        print("Failed to retrieve crumb. Cannot make API call to Jenkins in lieu of this. Exception: {}".format(e))
        return None

    # Adding crumb and Content-Type as header to api request
    headers = {
        "{}".format(crumb_field): "{}".format(crumb_value),
        "Content-Type":"application/xml"
    }
    print 'Crumb header build successfully '+ crumb_value
    return headers

def writeToFile(completeName, content):
    temp_file = open(completeName, "w")
    temp_file.write(content)
    temp_file.close()
    
def getPluginInfo(sourcepluginUrl,source_jenkins_username,source_jenkins_password):
    #Purpose: get list of plugins from source jenkins server and return pluginList[]={pluginshortName|version}
    pluginList=[]
    print 'Getting Plugin info from server "' + sourcepluginUrl +'"'
    response=requests.get(sourcepluginUrl,auth=(source_jenkins_username, source_jenkins_password),verify=False)
    response=response.json()
    if response['plugins'] == []:
        print 'No Data!'
    else:
        i=0
        for rows in response['plugins']:
            pluginShortName = rows['shortName']
            pluginVersion = rows['version']
            pluginList.insert(i, pluginShortName+'|'+pluginVersion)
            i=i+1        
    return pluginList
 
def createPluginBackup(source_jenkinsUrl,plugin_backup_path,source_jenkins_username,source_jenkins_password):
    #Purpose: create the backup of installed plugin list from source jenkins server
    print 'Creating backup of Plugin list from jenkins server "' +source_jenkinsUrl+'"'
    sourcepluginUrl = source_jenkinsUrl + "/pluginManager/api/json?depth=1"  #API call to get list of plugin
    pluginList=getPluginInfo(sourcepluginUrl,source_jenkins_username,source_jenkins_password)
    name_of_file = "PluginBackup"     
    completeName = os.path.join(plugin_backup_path, name_of_file + ".txt") 
    plugin_file = open(completeName, "w")
    for plugin in pluginList:
        #print 'Plugin Name '+ plugin
        plugin_file.write(plugin+'\n')
    plugin_file.close() 
    print 'Backup of Plugin list from jenkins server "' +source_jenkinsUrl+'" completed'   
       
def installPlugin(pluginShortName,header,destination_jenkinsUrl,destination_jenkins_username,destination_jenkins_password):
    #Purpose: install plugins by given pluginShortName on destination jenkins
    print 'Installing Plugin for "' + pluginShortName + '" on Jenkins server "' + destination_jenkinsUrl+'"'
    final_url = "{0}/pluginManager/installNecessaryPlugins".format(destination_jenkinsUrl)
    payload = '<jenkins><install plugin="{0}@latest"/></jenkins>'.format(pluginShortName) #Install plugin with latest version API call
    response = requests.post(final_url, data=payload, headers=header, auth=(destination_jenkins_username, destination_jenkins_password),verify=False) 
    if response.status_code==200 :  # HTTP
        print 'Plugin "' +pluginShortName+'" installed successfully'
    else:
        print 'Plugin "' +pluginShortName+'" creation failed'
        print 'Plugin Creation Failure status code : ' +str(response.status_code) 
   
def installPluginOnDestination(source_jenkinsUrl,source_jenkins_username,source_jenkins_password,header,destination_jenkinsUrl,destination_jenkins_username,destination_jenkins_password):
    #Purpose: Invoke Plugin Installation on destination jenkins server
    print 'Installing plugins on destination jenkins server "'+destination_jenkinsUrl+'"'
    sourcepluginUrl = source_jenkinsUrl + "/pluginManager/api/json?depth=1"  #API call to get list of plugin
    pluginList=getPluginInfo(sourcepluginUrl,source_jenkins_username,source_jenkins_password) #get the list of plugins to install
    for plugin in pluginList:
        pluginDetails=plugin.strip().split('|')
        pluginShortName=pluginDetails[0]
        installPlugin(pluginShortName,header,destination_jenkinsUrl,destination_jenkins_username,destination_jenkins_password)  #function to install plugin   
    print 'Installation of plugins on destination jenkins server "'+destination_jenkinsUrl+'" completed'
    
def getJobInfo(sourcejobUrl,source_jenkins_username,source_jenkins_password):
    #Purpose: get job list from source jenkins server and return jobList=[]{jobName|jobConfigUrl}
    print 'Getting list jobs from source jenkins server "'+sourcejobUrl+'"'
    jobList=[]
    response=requests.get(sourcejobUrl,auth=(source_jenkins_username, source_jenkins_password),verify=False)
    response=response.json()
    if response['jobs'] == []:
        print 'No Data!'
    else:
        j=0
        for rows in response['jobs']:
            #print 'JobName: ' + rows['name']
            #print 'JobURL: ' + rows['url']
            jobName = rows['name']
            jobUrl = rows['url']
            jobConfigUrl = jobUrl + "config.xml"
            jobList.insert(j,jobName+'|'+jobConfigUrl)
            j=j+1
            
    return jobList        
            
def getJobConfig(jobConfigUrl,source_jenkins_username,source_jenkins_password):
    #Purpose: get job config.xml file content from source jenkins server
    print 'Getting job config.xml from source jenkins server "'+jobConfigUrl+'"'
    response=requests.get(jobConfigUrl,auth=(source_jenkins_username, source_jenkins_password),verify=False)
    config_content = response.text
    return config_content

def createJobBackup(source_jenkinsUrl,job_backup_path,source_jenkins_username,source_jenkins_password):
    #Purpose: create the job config.xml backup from source jenkins server
    print 'Creating backup of job config.xml from source jenkins server "'+source_jenkinsUrl+'"'
    sourcejobUrl = source_jenkinsUrl + "/view/All/api/json"   #API call to get list of jobs
    jobList=getJobInfo(sourcejobUrl,source_jenkins_username,source_jenkins_password)
    for job in jobList:
        jobDetails=job.strip().split('|')
        jobName=jobDetails[0]
        jobConfigUrl=jobDetails[1]
        config_content=getJobConfig(jobConfigUrl,source_jenkins_username,source_jenkins_password)
        name_of_file = jobName    
        completeName = os.path.join(job_backup_path, name_of_file + "_config.xml")
        writeToFile(completeName, config_content)
    print 'Backup of job config.xml from source jenkins server "'+source_jenkinsUrl+'" completed'
    
def installJob(jobName,config_content,header,destination_jenkinsUrl,destination_jenkins_username,destination_jenkins_password):
    #Purpose: create and install jobs on destination jenkins server
    print 'Creating Job "' + jobName + '" on Jenkins server "' + destination_jenkinsUrl+'"'
    final_url = "{0}/createItem?name={1}".format(destination_jenkinsUrl, jobName)
    response = requests.post(final_url, data=config_content, headers=header, auth=(destination_jenkins_username, destination_jenkins_password),verify=False) 
    if response.status_code==200 :  # HTTP
        print 'Job "' +jobName+'" created successfully'
    else:
        print 'Job "' +jobName+'" creation failed'  
        print 'Job creation Failure status code : '+str(response.status_code)
                    
def installJobOnDestinationByCreatingBackup(source_jenkinsUrl,source_jenkins_username,source_jenkins_password,job_backup_path,header,destination_jenkinsUrl,destination_jenkins_username,destination_jenkins_password):
    #Purpose: Invoke Job installation on Destination Jenkins server 
    print 'Installing Jobs on destination Jenkins server "'+destination_jenkinsUrl+'"'
    #createJobBackup(source_jenkinsUrl, job_backup_path, source_jenkins_username, source_jenkins_password)
    for filename in glob.glob(os.path.join(job_backup_path, '*.xml')):
        f = open(filename, 'r')
        jobName=os.path.basename(filename)
        start=0
        end=len(jobName)
        jobName=jobName[start:end-11]  #to avoid '_config.xml' in Job Name
        config_content = f.read()
        f.close()
        installJob(jobName, config_content,header,destination_jenkinsUrl,destination_jenkins_username,destination_jenkins_password)
    print 'Installation of Jobs on destination Jenkins server "'+destination_jenkinsUrl+'" completed'                 

def installJobOnDestinationByUrl(source_jenkinsUrl,source_jenkins_username,source_jenkins_password,header,destination_jenkinsUrl,destination_jenkins_username,destination_jenkins_password):
    #Purpose: Invoke Job installation on Destination Jenkins server 
    print 'Installing Jobs on destination Jenkins server "'+destination_jenkinsUrl+'"'
    sourcejobUrl = source_jenkinsUrl + "/view/All/api/json"   #API call to get list of jobs
    jobList=getJobInfo(sourcejobUrl,source_jenkins_username,source_jenkins_password)
    for job in jobList:
        jobDetails=job.strip().split('|')
        jobName=jobDetails[0]
        jobConfigUrl=jobDetails[1]
        config_content=getJobConfig(jobConfigUrl,source_jenkins_username,source_jenkins_password)
        installJob(jobName, config_content,header,destination_jenkinsUrl,destination_jenkins_username,destination_jenkins_password)
    print 'Installation of Jobs on destination Jenkins server "'+destination_jenkinsUrl+'" completed'                 
