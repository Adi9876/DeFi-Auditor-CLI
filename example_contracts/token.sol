// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity ^0.8.24;

contract Token {
    uint256 public count;
    uint256 public total;

    constructor(uint256 _count) {
        count = _count;
    }

    function increaseCount() public {
        count++;
    }


    function sumArray(uint256[] calldata values) public {
        for (uint256 i = 0; i < values.length; i++) {
            total += values[i];
        }
    }
}
