\# StreamlineCorp Leave Management

\## Release Notes – Version 1.0.0



\*\*Release date:\*\* 29 September 2026



\### Overview



Version 1.0.0 provides the first MVP release of the StreamlineCorp Employee Leave Management feature. The release supports employee leave requests, HR review and basic role-based authorisation.



\### Features



\- Employees can submit Annual, Sick and Unpaid Leave requests.

\- Working days are calculated using Monday–Friday working patterns.

\- Employees can view their leave request history and current status.

\- Requests are validated for invalid dates, past dates and insufficient Annual Leave balance.

\- Overlapping Pending or Approved requests are prevented.

\- HR users can review, approve and reject Pending requests.

\- Approved Annual Leave is deducted from the employee's remaining entitlement.

\- HR functions are protected using server-side role checks.

\- Employee and HR interfaces include accessibility-conscious design features.



\### Testing



The release was tested using manual functional testing and an automated PyTest suite.



The automated suite contains 11 tests covering:



\- valid leave requests;

\- invalid leave types;

\- invalid date ranges;

\- past-date requests;

\- insufficient leave entitlement;

\- exact-balance boundary behaviour;

\- working-day calculation;

\- employee denial from HR functionality;

\- successful HR access;

\- invalid HR actions; and

\- prevention of employee approval actions.



All 11 automated tests passed before release.



\### Accessibility



The interface includes accessibility-conscious design decisions, including:



\- explicit form labels;

\- visible keyboard focus states;

\- semantic table headings;

\- written status labels in addition to colour;

\- responsive layouts; and

\- live feedback messaging.



Key colour combinations were checked against WCAG contrast requirements and met the WCAG AA minimum for normal text.



\### Known Limitations



\- Authentication is simulated for the MVP and is not suitable for production use.

\- SQLite is used as a local database and is not intended as the final enterprise data platform.

\- Working-day calculations exclude weekends but do not account for public holidays or individual working patterns.

\- The MVP contains Employee and HR roles only.

\- Production deployment infrastructure, SSO and enterprise monitoring are outside the scope of this release.

