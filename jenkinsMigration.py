import performTask
from os import listdir
from os.path import isfile, join

if __name__ == "__main__":
    #Read user inputs from resource.txt file
    #resource.txt : {source_jenkins_username,source_jenkins_password,source_jenkins_url,system_folder_path_to_save_pluginInfo.txt_file,system_folder_path_to_save_jobConfig_file,destination_jenkins_username,destination_jenkins_password,destination_jenkins_url,destination_user_token}
    f = open("resource.txt", "r")
    lines = []
    for line in f:
        line = line.strip()
        lines.append(line)
    f.close()

    source_jenkins_username = lines[0]
    source_jenkins_password = lines[1] 
    source_jenkinsUrl = lines[2]
    destination_jenkins_username = lines[3]
    destination_jenkins_password = lines[4] 
    destination_jenkinsUrl = lines[5]
    destination_jenkins_token = lines[6]
    plugin_backup_path = lines[7]
    job_backup_path = lines[8]
    header = performTask.getCrumbHeader(destination_jenkinsUrl, destination_jenkins_username, destination_jenkins_token)
    
    while True:
        print("\nMenu\n(1) Plugin Migration\n(2) Job Migration\n(3) Quit")
        choice =int(raw_input("Enter choice: ").strip())
        if choice==3:
            print 'Exiting Menu'
            break
        elif choice==1:
            print("\nPlugin Migration Sub-Menu\n(1) Create Plugin Backup\n(2) Install Plugins")
            subchoice = int(raw_input("Enter choice: ").strip())
            if subchoice==1:
                print '\nChoice (1) Create Plugin Backup selected'
                performTask.createPluginBackup(source_jenkinsUrl, plugin_backup_path, source_jenkins_username, source_jenkins_password)
            elif subchoice==2:
                print '\nChoice (2) Install Plugins selected'
                performTask.installPluginOnDestination(source_jenkinsUrl, source_jenkins_username, source_jenkins_password, header, destination_jenkinsUrl, destination_jenkins_username, destination_jenkins_password)
            else:
                print("Invalid choice, please choose again\n")        
        elif choice==2:
            print("\nJob Migration Sub-Menu\n(1) Create Job Backup\n(2) Install Jobs")
            subchoice = int(raw_input("Enter choice: ").strip())
            if subchoice==1:
                print '\nChoice (1) Create Job Backup selected\n'
                performTask.createJobBackup(source_jenkinsUrl, job_backup_path, source_jenkins_username, source_jenkins_password)
            elif subchoice==2:
                print '\nChoice (2) Install Jobs selected'
                print("\nInstall Job Sub-Menu\n(1) Install Job using existing config files backup\n(2) Install Jobs using get Job Config API")
                subchoice = int(raw_input("Enter choice: ").strip())
                if subchoice==1:
                    print '\nChoice (1) Install Job using existing config files backup selected'
                    if any(fname.endswith('.xml') for fname in listdir(job_backup_path)):
                        performTask.installJobOnDestinationByCreatingBackup(source_jenkinsUrl, source_jenkins_username, source_jenkins_password,job_backup_path, header, destination_jenkinsUrl, destination_jenkins_username, destination_jenkins_password)
                    else:
                        print 'No backup config.xml files exist'  
                elif subchoice==2:
                    print '\nChoice (2) Install Jobs using getJob Config API'
                    performTask.installJobOnDestinationByUrl(source_jenkinsUrl, source_jenkins_username, source_jenkins_password, header, destination_jenkinsUrl, destination_jenkins_username, destination_jenkins_password)
                else:
                    print("Invalid choice, please choose again\n")    
            else:
                print("Invalid choice, please choose again\n")
        else:
            print("Invalid choice, please choose again\n") 