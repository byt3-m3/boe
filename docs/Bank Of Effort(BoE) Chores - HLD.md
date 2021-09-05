# Bank Of Effort(BoE) Chores

Possible Names:

- Acheivement Bank 
- Bank of Effort 
- Bank of Excellence 



## Overview 

BOE is a application that provides parents a method of teaching and enoforcing value concepts to their children. BoE core focus is to provide a method to enable parents to provide a list of tasks with associated values that parents to assign to their children.  Upon completion of these tasks, The child will be awarded compensation that can be utilized to purchase pre-defined items. The store items will be pre-configured by the parents and will be present a central store for the child to purchase items.

## Business Model 

BOE will utilize a subscription model that will enable free and premium users access to basic service features, with Premium Users giving additional features.



### Standard Users 

- Limit 2 children per family
- Limit 5 assigned children per 

### Premium Users 

## Functional Requirements

### Child Requirements

- As a child I would like to mark my task complete so that I can be compensated for my efforts.

- As a child I would like to receive notifications so that if my parents assingment me new tasks I can be aware .

- As a child I would to be able to check my account balance on demend so that I can be aware of my balance.

- As  a child I like to purchase items from the store with using balance from my bank account so that I can spend my effortcash as Id like.

- As a child I would like to be able to provide evidence that my task is complete by uploading a photo so that I can notify  my parents of my work. 

  

### Parent Requirments 

- As a parent I would like to assign my child task, so that I can automate their chores. 
- As a parent I would like to track my childs completed tasks, so that I can better understand how they spend their time.
- As a parent I would to create items in the store so that my child can use their bank balance to purchas them. 
- As a parent I would like to receive notifications when my child completes a task. 
- As a parent I would like to have tasks that can  be verified by notifcations so that I can ensure my childs taks is completed. 

### Bank Requirements 

- As a bank, I would like to keep track of my owners balance so that I provide accurate account information 
- As a bank I would like to keep each account unique to its child so that they keep track their individual balance.. 
- As a bank I would the ability for customers to transfer balances between their accounts so that they can use their own bargining strategies.  

### Store Requirements 

- As a store I would like to be centrally accessible, so that children and parents of the system can access me at all times. 

  

## MVP 





## Design 

### Roles 

Family 

Parent 

Child 



### Domains  

**Bank**

The bank domain handles all responsibility related to account management. 

Enums

```python
class AccountStatus(Enum):
    ACTIVE = 1
    INACTIVE = 2
    OVER_DRAFTED = 3
 
class TransActionMethodEnum(Enum)
		ADD = 1
		SUBTRACT = 2
    
class PermissionsEnum(Enum):
  Admin = 0
  
```



Data Models 

```python
from dataclasses import dataclass 


@dataclass
class TransactionValue:
  value: float

```





Aggregates 

```python
from dataclasses import dataclass 

@dataclass
class AccountOwner(Aggregate):
  name: str 
    
  class ChangeNameEvent(AggregateEvent):
    value: str 

@dataclass
class AccountAdmin(Aggregate):
  name: str 
  permission_map: Dict[str, PermissionsEnum]
    
  class AddPermissionEvent(AggregateEvent):
    permission: PermissionsEnum
  
  class DeletePermissionEvent(AggregateEvent):
    permission_id: UUID
  
  
@dataclass
class AccountAggregate(Aggregate):
  balance: float 
  owner: AccountOwner
  status: AccountStatusEnum
  admins: List[AccountAdminAggregate]
    
  class ChangeAccountbalanceEvent(AggregateEvent):
    transaction_method: TransactionMethodEnum
    new_value: float 
    admin: AccountAdmin
      
  class ChangeAccountStatusEvent(AggregateEvent):
    admin: AccountAdmin
    status: AccountStatus
      
  class AddAccountAdminEvent(AggregateEvent):
    admin: AccountAdmin
    new_admin: AccountAdmin
      
  class RemoveAccountAdminEvent(AggregateEvent):
    admin: AccountAdmin
    admin_id: UUID 
      
  class SetAccountOwnerEvent(AggregateEvent):
    admin: AccountAdmin
    owner: AccountOwner
      
  class SetAccountClosedEvent(AggregateEvent):
    pass 
    
```



DataModels:

- TransactionValue
  - Properties
    - data

Aggregates:  

- BankAccountAggregate 

  - Properites
    - Balance: float 
    - Owner: AccountOwnerAggregate 
    - Admins: List[AccountAdminAggregate]
    - Status:  AccountStatusEnum
  - AggregateEvents:
    - CreateEvent
    - CloseAccountEvent
    - SetAccoutOwnerEvent
    - AddAccountAdminEvent
    - RemoveAccountAdminEvent
    - ChangeAccountbalanceEvent
    - ChangeAccountStatusEvent

- AccountAdminAggregate

  - Properties:
    - name
  - AggregateEvents: 
    - ChangeNameEvent
    - AddPermissionEvent 

- AccountOwnerAggregate 

  - AggregateEvents 

    - CreatEvent

    - ChangeUserNameEvent

    - AddPermissionEvent 

      

- TransactionAggregate

  - Properites
    - Method: TransactionMethodEnum 
    - values: List[TransactionValue]

Enum:

- AccountStatusEnum
  - ACTIVE
  - INACTIVE 
  - OVERDRAFTED 
- PermissionsEnum
- TransactionMethodEnum
  - ADD
  - SUBTRACT



**Chore Libarary ** 

**Tasks** 

Aggregates:

- AsigneeAggregate 
  - Properties:
    - Name: str 
    - FamilyName: str 

- TaskAggregate
  - Properties:
    - Name: str 
    - Description: str 
    - Status: TaskStatusEnum
    - Value: int 

Enums

- TaskStatusEnum 
  - PendingVerification
  - Complete
  - Assigned 
  - In-Progress 
  - Rejected 

**Store**