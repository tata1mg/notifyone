<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tata1mg/notifyone/master/media/logo.png">
    <img src="https://raw.githubusercontent.com/tata1mg/notifyone/master/media/logo.png" width="300" alt="Logo"/>
  </picture>
</div>
<h1 align="center">An open-source, event-based notification system for everyone</h1>
<div align="center">
The ultimate solution for a scalable, multi-channel notification system
</div>

## ⭐️ Why NotifyOne?

NotifyOne provides an event driven notification system that exposes a unified API to trigger multi channel notifications including Email, Sms, Push and Whatsapp.

It lets you define an event in the system and configure different channels of notifications for that event.

## ✨ Features
- Event-based notification system.
- Low, medium, high, and critical priorities for the events to make sure important notifications are prioritized in the system.
- Built upon open-source tech stack.
- Supports all the important channels for notifications - email, sms, push, WhatsApp and VoIP (**VoIP to be supported in future releases**).
- Highly scalable. Decoupled components for different tasks (gateway, rendering, and operator integration are decoupled which enables it to scale different components differently based on need).
- Easy to set up and integrate - ideal for both stand-alone and container-based deployments
- Equipped with CMS for creating advanced templates (Uses Jinja2 as templating engine) and reporting. (**WIP - to be released in future releases**)
- Highly configurable - Add/Remove operators(service providers) for different channels with ease, change priority between operators, define custom priority logic to handle rare business use cases, all this with just a few clicks.
- Fault-tolerant - usages queuing as and when needed for a fault-tolerant architecture. Provides automatic switching between different operators for a channel based on their performance.

## :ballot_box_with_check: Providers Supported
Currently, we support below list of providers for different channels. More providers will be added with the future releases.

If you wish to have a provider for a channel that is not in the list, feel free to integrate it and raise a PR.
#### :envelope: EMAIL
- [x] SparkPost
- [x] AWS SES

#### :memo: SMS
- [x] SMS Country
- [x] Plivo
- [x] AWS SNS

#### :iphone: PUSH
- [x] FCM

#### :pager: WhatsApp
- [x] Interakt

## The Architecture
NotifyOne uses a highly scalable, fault-tolerant architecture. It runs as a group of services that, combined together, work for the best performance.

NotifyOne has been architected keeping in mind the actual production load and deployment strategies. The components have been decoupled keeping in mind the tasks they perform and their scaling needs.

The NotifyOne system has been seen as an integration of it's four core components - 

1. [Gateway](https://github.com/tata1mg/notifyone-gateway) - This is a light-weight components that exposes APIs for sending notifications and retriving notification statuses. It works as a single point of contact to the NotifyOne system for the outside world. 
2. [Core](https://github.com/tata1mg/notifyone-core) - This is where the actual magic happens. Core component is responsible for `app` and `event` management, `template` creation and editing, `template` rendering, routing notification request for a channel to the designated handler, logging notification request etc. It also servers as the backend service to the NotifyOne CMS (Admin Panel)  
3. [Handlers](https://github.com/tata1mg/notifyone-handler) - This component provides integrations with the actual operator gateways like Plivo and SmsCountry for sms, SparkPost and SES for email etc. This component supports multi channel deployment which means handle for each channel can also be deployed as a seprate service. Please refer to the service documentation for more detils.  
4. CMS - (**WIP**) This is admin panel of our NotifyOne system. It provides event and app management, template management, operator and priority logic configurations, analytics and reporting. This component is currently under development and will be released soon in futre releases.

#### # architecture diagram 

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tata1mg/notifyone/master/media/architecture.png">
    <img src="https://raw.githubusercontent.com/tata1mg/notifyone/master/media/architecture.png" width="1000" alt="Logo"/>
  </picture>
</div>

- The architecture makes it easy to introduce a new channel or integrate with new providers.
- Gateway, Core and Handlers can be scaled independently based on needs.

## 🚀 Getting Started
#### Tools & Technologies you need before getting started 
- Postgres DB
- Redis
- AWS SQS
- AWS S3

The NotifyOne repository itself does not contain any code and implementations for all the components can be found in their respective repositories.

### Quick try-out ?
We have created a script [notify_setup.py]() that can be used to setup the services quickly on your local system. The script sets up the `notifyone-gateway`, `notifyone-core` and `notifyone-handler` services quickly on your machine (it automatically installs dependencies and resolves connectivity between services).    

#### Prerequisites
- Docker : your machine must have docker installed and running.
- Python - your machine must have python version >= 3.7 installed on it.

#### How to?
- Clone the [NotifyOne](https://github.com/tata1mg/notifyone) project
  - git clone https://github.com/tata1mg/notifyone.git
- `cd` to notifyone directory
  - cd notifyone
- Run command -
  - python3 notify_setup.py

### Production like deployment?
- Clone the [NotifyOne](https://github.com/tata1mg/notifyone) project
  - `git clone https://github.com/tata1mg/notifyone.git`
- `cd` to notifyone directory
  - `cd notifyone`
- Components are available as git submodule in the notifyone repo. So we need to `init` and `update` the submodules-
  - `git submodule init`
  - `git submodule update`
- Deploy the Gateway, Core and Handlers components as per your preference (help on how to deploy can be found in respective repositories README.md)
- Create test App and Event - Use APIs exposed in Core service to create a test App and Event
- Trigger notification - use the Gateway's "send-notification" API to trigger notifications for the test Event created in step 2.

## Contribution guidelines
Please refer to our [Contribution Guidlines](https://github.com/tata1mg/notifyone/blob/master/CONTRIBUTING.md) before for more details.

## License
This project is licensed under the
[Apache-2.0](https://github.com/tata1mg/notifyone/blob/master/LICENSE) License.