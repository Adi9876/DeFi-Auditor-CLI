// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract VulnerableBank {
    mapping(address => uint256) public balances;

    // Deposit ether into the contract
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // Withdraw function is vulnerable to reentrancy
    function withdraw(uint256 _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // Vulnerable: sending ether before updating balance
        (bool sent, ) = msg.sender.call{value: _amount}("");
        require(sent, "Failed to send Ether");

        balances[msg.sender] -= _amount;
    }

    // Allow owner to set any user's balance — no access control!
    function setBalance(address user, uint256 _amount) public {
        balances[user] = _amount;
    }

    // Self-destruct with no restrictions
    function kill() public {
        selfdestruct(payable(msg.sender));
    }

    // HIGH VULNERABILITY: Unsafe delegatecall function
    function executeDelegateCall(address _target, bytes calldata _data) public {
        // No access control or validation
        (bool success, ) = _target.delegatecall(_data);
        require(success, "Delegatecall failed");
    }
}
