'''
Self Check Agent
'''

class SelfCheckAgent():
    '''
    Self Check Agent
    Check alex's current status based on the observation, code info, done and task info. Return the next step and description.
    '''
    def __init__(self, 
                 FAILED_TIMES_LIMIT = 5,
                 save_path = None):
        self.FAILED_TIMES_LIMIT = FAILED_TIMES_LIMIT
        self.code_error_count = 0
        self.save_path = save_path

    def self_check(self, obs, code_info = None, done = None, task_info = None, associative_memory = None):
        '''
        params:
            obs: observation
            code_info: code info
            done: is task done
            task_info: task info
            
        return:
            next_step: next step
            description: description
        '''

        next_step = None
        description = None

        # 1. Task Check
        if done is True:
            description = "Task Succeed" if task_info.is_success else "Task Failed"
            next_step = None
            return next_step, description

        # 2. Special Event Check
        if len(obs['event']) > 0:
            sender = "<" + obs["name"] + ">"
            for event in obs['event']:
                if event['type'] == 'chat' and not event['message'].startswith(sender) and obs["name"] in event['message']:
                    description = "Special Event"
                    next_step = "brain"
                    break
                if event['type'] == 'entityHurt' and obs['name'] in event['message']:
                    description = "Special Event"
                    next_step = "brain"
                    break

        code_timeout = None

        if code_info["code_tick"] >= 500:
            code_timeout = code_info
            description = "Special Event"
            next_step = "brain"

        if description == "Special Event":
            special_event_check = associative_memory.special_event_check(obs, task_info, code_timeout)
            print(f"\033[31m****Special Event Check****\n{special_event_check}\033[0m")
            if special_event_check["handling"]:
                self.code_error_count = 0
                return next_step, description
                
        # 3. Code Check
        if code_info and code_info.code_error:
            self.code_error_count += 1
            if self.code_error_count >= self.FAILED_TIMES_LIMIT:
                description = "Code Failed"
                next_step = "brain"
                self.code_error_count = 0
                return next_step, description
            else:
                description = "Code Error"
                next_step = "action"
                return next_step, description
        
        if code_info and code_info.is_running:
            description = "Code Unfinished"
            next_step = "action"
            self.code_error_count = 0
            return next_step, description

        description = "Ready"
        next_step = "critic"
        self.code_error_count = 0
        return next_step, description
    