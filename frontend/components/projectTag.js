"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

const alphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

const getRandomInt = (max) => Math.floor(Math.random() * max);

export function HyperText({
  text,
  duration = 800,
  framerProps = {
    initial: { opacity: 0, y: -10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 3 },
  },
  className = "",
  animateOnLoad = true,
}) {
  const [displayText, setDisplayText] = useState(text.split(""));
  const [trigger, setTrigger] = useState(false);

  const iterations = useRef(0);
  const isFirstRender = useRef(true);

  const triggerAnimation = () => {
    iterations.current = 0;
    setTrigger(true);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      if (!animateOnLoad && isFirstRender.current) {
        clearInterval(interval);
        isFirstRender.current = false;
        return;
      }

      if (iterations.current < text.length) {
        setDisplayText((current) =>
          current.map((letter, index) =>
            letter === " "
              ? letter
              : index <= iterations.current
              ? text[index]
              : alphabets[getRandomInt(26)]
          )
        );

        iterations.current += 0.1;
      } else {
        setTrigger(false);
        clearInterval(interval);
      }
    }, duration / (text.length * 10));

    return () => clearInterval(interval);
  }, [text, duration, trigger, animateOnLoad]);

  return (
    <div
      className="flex scale-100 cursor-default overflow-hidden py-2"
      onMouseEnter={triggerAnimation}
    >
      <AnimatePresence mode="wait">
        {displayText.map((letter, index) => (
          <motion.span
            key={index}
            className={`font-mono ${letter === " " ? "w-3" : ""} ${className}`}
            {...framerProps}
          >
            {letter.toUpperCase()}
          </motion.span>
        ))}
      </AnimatePresence>
    </div>
  );
}


// --- Demo ---
import { HyperText } from "@/components/ui/hyper-text"

export function HyperTextDemo() {
  return (
    <HyperText
      className="text-4xl font-bold text-black dark:text-white"
      text="Hyper Text"
    />
  );
}
