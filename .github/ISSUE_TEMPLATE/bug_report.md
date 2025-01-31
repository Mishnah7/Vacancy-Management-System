---
name: Bug report
about: Create a report to help us improve
title: 'JobDeleteAPIView: Improper Exception Handling in Job Deletion'
labels: 'bug, backend'
assignees: ''

---

**Checklist**

- [x] I have verified that that issue exists against the `master` branch.
- [x] I have searched for similar issues in both open and closed tickets and cannot find a duplicate.
- [x] I have reduced the issue to the simplest possible case.

**Describe the bug**
In the `JobDeleteAPIView` class within `jobsapp/api/views/employer.py`, there is a bug in the exception handling logic for job deletion. The code structure has nested try-except blocks that could lead to attempting operations on non-existent jobs and unclear error handling paths.

**Specify the team with the correct label**
Backend Team

**To Reproduce**
Steps to reproduce the behavior:
1. Access the job deletion endpoint with an invalid job ID
2. Observe that while the code returns a 404, the logs show that the code attempts to proceed with deletion operations
3. Check the logs to see confusing or inconsistent error messages due to nested exception handling

**Expected behavior**
When a job is not found:
1. The code should immediately return a 404 response
2. No further operations should be attempted
3. The logs should clearly indicate the job was not found without any additional processing attempts
4. The error handling should be clear and in a single try-except block structure

**Code Location**
File: `jobsapp/api/views/employer.py`
Class: `JobDeleteAPIView`
Method: `delete()`

**Current Implementation**
```python
def delete(self, request, job_id):
    logger.info("="*50)
    logger.info("JOB DELETION ATTEMPT")
    logger.info("="*50)
    
    try:
        # Get the job
        try:
            job = Job.objects.select_related('user').get(id=job_id)
            logger.info(f"Job found - ID: {job_id}")
        except Job.DoesNotExist:
            logger.warning(f"Job {job_id} not found")
            return JsonResponse(
                {"error": "Job not found"},
                status=404
            )
        
        # Delete the job
        logger.info("Permission checks passed, proceeding with deletion")
        job.delete()
        # ... cache clearing code ...
        
    except Exception as e:
        logger.error("Unexpected error during job deletion")
        logger.error(f"Error type: {type(e).__name__}")
        return JsonResponse(
            {"error": "Failed to delete job. Please try again."},
            status=500
        )
```

**Desktop (please complete the following information):**
 - OS: Linux 6.8.0-52-generic
 - Browser: N/A (API Endpoint)
 - Version: N/A

**Additional context**
This is a backend API issue that affects the job deletion endpoint. The bug could potentially cause confusion in error handling and logging, making it harder to debug issues in production. The fix has already been implemented by restructuring the exception handling into separate, clear blocks.