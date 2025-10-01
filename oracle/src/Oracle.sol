pragma solidity >=0.8.30;


struct Message {
    uint128 value;
    uint block;
    address sender;
    bool isAuthorized;
}

contract Oracle {
    bytes21 public roflAppId;
    
    Message[] public messages;

    constructor(bytes21 _roflAppId) {
        roflAppId = _roflAppId;
        messages = new Message[](0);
    }

    function submitMessage(uint128 _value) external {
        messages.push(Message(_value, block.number, msg.sender, true));
    }

    function getLastMessage() external view returns (Message memory) {
        if (messages.length == 0) {
            return Message(0, 0, address(0), false);
        }
        return messages[messages.length - 1];
    }

    function getMessages() public view returns (Message[] memory) {
        return messages;
    }

    function getMessagesBySender(address _sender) external view returns (Message[] memory) {
        // First, count how many messages match
        uint count = 0;
        for (uint i = 0; i < messages.length; i++) {
            if (messages[i].sender == _sender) {
                count++;
            }
        }
        
        // Create array with correct size
        Message[] memory _messages = new Message[](count);
        uint index = 0;
        for (uint i = 0; i < messages.length; i++) {
            if (messages[i].sender == _sender) {
                _messages[index] = messages[i];
                index++;
            }
        }
        return _messages;
    }

    function getAuthorizedMessages() public view returns (Message[] memory) {
        // First, count how many messages are authorized
        uint count = 0;
        for (uint i = 0; i < messages.length; i++) {
            if (messages[i].isAuthorized) {
                count++;
            }
        }
        
        // Create array with correct size
        Message[] memory _messages = new Message[](count);
        uint index = 0;
        for (uint i = 0; i < messages.length; i++) {
            if (messages[i].isAuthorized) {
                _messages[index] = messages[i];
                index++;
            }
        }
        return _messages;
    }

    function numberOfMessages() external view returns (uint) {
        return messages.length;
    }

    function numberOfAuthorizedMessages() external view returns (uint) {
        return getAuthorizedMessages().length;
    }
}
