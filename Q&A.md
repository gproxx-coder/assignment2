### Q&A: Assignment 2

#### 1. Write a program in python to process logs
- Please find the instructions to run the program inside **readme.md** file

--------

#### 2. Explain your dev environment you'd setup for your project (what tools you use to help in dev productivity)?

- Below is my dev environment
  - OS: Windows 10 
  - Code Editor: PyCharm
  - AWS-SDK: AWS Cli & Boto3 
  - Package Manager: Pip3 
  - Python Version: 3.10
- For the productivity I use
  - cProfile module
  - Type hints
  - Pycharm, VS Code, Jupyter Notebook
  - JSONLint
  - Sublime Text & Notepad++
  - Git, Github
  - Various IDE Extensions (Json, Yaml, CSV, Docker, etc)
  - Reading Documentations

--------

#### 3. Explain how we can scale this solution for large number of files - 10000-20000+ log files.
- Below can be some ways for scaling
  - Reading files in chunks (like some specific bytes)
  - Parallel Computing (Multiprocessing/Async) 
  - Using Celery workers along with RabbitMQ
  - Using messaging queues
  - Using pyspark to process logs
  - Using distributed processing

--------

#### 4. Explain what considerations you took to choose this approach only?
  1. using **"https://"** to filter out logs instead just using **"https"**, because if logfile has some
    malformed data that starts with **"httpsjdhj"** then it will be collected by program, which is not correct.
    so used fully qualified keyword **"https://"**
  2. Reading file in following pattern: "log*.md"
     - Filename should start with **log** and end with **.md**
       - If some invalid filename comes like **log.jpg** then we will not consider it
       - Valid filenames: log.md, logs.md, log123.md, log_234.md, etc
       - Invalid filename: log, log.txt, log123, log.jpg, etc
  3. Using string **slicing** over **startswith()** function:
     - I tested slicing and startswith() with 50000 lines of input log file.
       The avg time for slicing & startswith() was 0.042 & 0.062 seconds respectively.
       also startswith() works good for very long strings but not small, So I chose **slicing**.
  4. For uploading file to S3 we have 2 options
     - **s3_client.upload_file** - uploads a file from local disk 
     - **s3_client.upload_fileobj** - accepts a readable file-like object. The file object must be opened in binary mode, not text mode.
     - I chose **s3_client.upload_file** because it handles large files by splitting them into smaller chunks and uploading each chunk in parallel.
     - Though **upload_file** and **upload_fileobj** methods are provided by the S3 Client, Bucket, and Object classes.
       The method functionality provided by each class is identical.
     - No benefits are gained by calling one class's method over another's. Use whichever class is most convenient.
  5. Folder structure in S3 as follows:
     - **<bucket-name>/logs/<log-type>/<current-date>/<current-time>_<log-type>_logs.md**
  6. Using dictionary which will have 3 keys (https, http, ftp) and the values will be
    list of urls. Easy to manage.
  7. Used generator function instead of direct list
  8. Creating folders if it does not exist, and we don't need to worry about exceptions if someone deletes.

--------

#### 5. Explain if any alternatives approaches can be considered to solve the same problem?
- Below can be some alternative approaches
  - Using **s3_client.upload_fileobj** function instead of **s3_client.upload_file** if we want to
    directly upload file from memory instead of hard drive to S3 bucket.
  - S3 File name and Folders structure can be changed according to needs. Instead of using timestamp,
    we can also use some unique id as filenames.
  - Used direct lists instead of using a generator function
  - If urls are too long then we can also use Using **startswith()** function over string **slicing**
  - Instead of considering only log files with **.md** extension, we can also allow to read from **.txt**
  - We can use Multiprocessing to create multiple processes, each process will execute 1 log type
  - We can use Celery Workers with Messaging Queue (RabbitMQ) to do background tasks like uploading files to S3
  - We can use pyspark to process logs (using pyspark startsWith() or when() function)

--------

#### 6. Explain steps as to where we should publish and deploy this code?
  1. Deploy as Lambda function (Can be triggered using EventBridge or some API call, etc)
     - It is managed service, so we just need to select Runtime (Python) and for dependencies
       we need to use Lambda Layers OR Need library in zipped format in local dir of Lambda on AWS.
  2. Package code using **.tar.gz** or **.zip** and copy to EC2 using scp and run it there.
     - Need to have Python and Pip install, then install dependencies (shown in Readme.md file).
  3. Create a repository on GitHub, Push the code. Go to the server where you want to execute this,
    Pull the code and Execute.
     - Need to have git installed and also need to install python and dependencies using pip.
  4. Write a Dockerfile, Build docker image from it. Push docker image to Dockerhub or ECR,
    then pull that docker image and run it inside EC2 or any server
     - Need to have Docker installed (Dependencies will be installed inside a container)
  5. Deploy as Glue function
     - It is managed service, so we just need to select Runtime (Python or Pysprak)
  6. Deploy within a cluster for distributed processing (e.g. EMR)

--------

#### 7. Explain best practices you considered while making this project?
  - Used virtual environment (using venv module)
  - Made code compatible working with multiple log input files
  - Profiling using cProfile
  - One Function One Task
  - Appropriate variable/function names
  - Type Hints using typing module
  - Exception Handling wherever possible
  - Unit Testing
  - DRY principle
  - KISS principle
  - Clean code
  - Followed PEP8 standards
  - Proper documentation
    - How to run
    - Environment setup
    - Docstrings wherever applicable

--------

#### 8.Explain any edge-case scenarios you considered and how tests can help with that?
  - Test read_log_file function whether it read files and returns output as dictionary or not
  - Test log_generator function whether it returns generator object or not
  - Test file_writer function whether it writes file to local disk or not
  - Test get_all_log_files to check whether it is returning all log files present in that folder or not
  
--------

#### Note: Please do not delete files present in mock_data folder