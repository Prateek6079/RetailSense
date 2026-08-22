'use client';

import React from 'react';

const InputBox = React.forwardRef(
  ({ id, label, className = '', ...props }, ref) => {
    return (
      <div className="relative w-full">
        <input
          ref={ref}
          id={id}
          placeholder="Enter Simulation Name"
          className={`
            peer
            block
            w-full
            rounded-md
            border
            border-gray-300
            bg-transparent
            px-3
            py-3
            text-sm
            outline-none
            transition
            placeholder-transparent
            focus:placeholder-gray-500
            ${className}
          `}
          {...props}
        />

        <label
          htmlFor={id}
          className="
            absolute
            left-3
            top-3
            cursor-text
            bg-black
            px-1
            text-sm
            text-white
            transition-all
            duration-200
            peer-focus:-top-2
            peer-focus:left-2
            peer-focus:text-xs
            peer-not-placeholder-shown:-top-2
            peer-not-placeholder-shown:left-2
            peer-not-placeholder-shown:text-xs
          "
        >
          {label}
        </label>
      </div>
    );
  }
);

InputBox.displayName = 'InputBox';

export default InputBox;