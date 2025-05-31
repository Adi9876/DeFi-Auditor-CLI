// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity ^0.8.24;

contract Token {
    uint256 public count;

    constructor(uint256 _count) {
        count = _count;
    }

    function increaseCount() public {
        count++;
    }
}
