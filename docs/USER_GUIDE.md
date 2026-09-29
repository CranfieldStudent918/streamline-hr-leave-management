\# StreamlineCorp Leave Management

\## User Guide – Version 1.0.0



\### Employee Dashboard



The Employee Dashboard provides an overview of:



\- the employee's name;

\- current Annual Leave balance;

\- number of leave requests; and

\- leave request history.



Each leave request displays:



\- leave type;

\- start date;

\- end date;

\- number of working days; and

\- current status.



Possible statuses are:



\- \*\*Pending\*\*

\- \*\*Approved\*\*

\- \*\*Rejected\*\*



\### Submitting a Leave Request



1\. Open the Employee Dashboard.

2\. Select \*\*Request Leave\*\*.

3\. Choose the required leave type.

4\. Enter the start date.

5\. Enter the end date.

6\. Optionally provide a reason.

7\. Select \*\*Submit leave request\*\*.

8\. Review the confirmation message.

9\. Return to the Dashboard to view the request status.



A successful new request is created with a \*\*Pending\*\* status.



\### Leave Request Validation



The system checks that:



\- the selected leave type is valid;

\- the end date is not before the start date;

\- the start date is not in the past;

\- Annual Leave does not exceed the available entitlement; and

\- the requested dates do not overlap an existing Pending or Approved request.



If validation fails, an explanatory message is displayed and the request is not saved.



\### HR Review



HR users can access the HR Dashboard to review Pending leave requests.



For each Pending request, HR can:



\- review the employee name;

\- review the leave type;

\- review the requested dates;

\- review the number of working days;

\- review the reason provided; and

\- choose \*\*Approve\*\* or \*\*Reject\*\*.



When Annual Leave is approved, the number of working days is deducted from the employee's Annual Leave balance.



Processed requests cannot be processed again.



\### Access Control



HR functionality is protected using server-side role checks.



Employee users attempting to access HR-only functionality receive an access-denied response.



For demonstration purposes, the MVP uses simulated user switching:



\- Employee user: Alex Morgan

\- HR user: Sam Taylor



This simulated switching mechanism is not intended to represent production authentication.



\### Accessibility



The interface includes:



\- clear labels for form controls;

\- visible focus indicators for keyboard navigation;

\- status text in addition to colour;

\- readable spacing and visual hierarchy;

\- responsive layouts; and

\- semantic table headings.



\### MVP Limitations



Version 1.0.0 is a local MVP and has several limitations:



\- authentication is simulated;

\- SQLite is used for local data storage;

\- public holidays are not included in working-day calculations;

\- individual working patterns are not supported;

\- only Employee and HR roles are included; and

\- production SSO, hosting, monitoring and enterprise deployment are outside the MVP scope.

