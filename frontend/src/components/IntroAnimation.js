import React, { useState, useEffect } from "react";

const IntroAnimation = ({ onComplete }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // After 2 seconds (time for all words to show), slide the intro away
    const timer = setTimeout(() => {
      setIsVisible(false);
      // Wait for slide-out animation to complete, then notify parent
      setTimeout(() => {
        onComplete();
      }, 800);
    }, 2000);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div
      className={`fixed inset-0 z-50 bg-black flex items-center justify-center transition-transform duration-800 ease-in-out ${
        isVisible ? "translate-y-0" : "-translate-y-full"
      }`}
    >
      {/* Animated Grid Background */}
      <div className="absolute inset-0 bg-grid-pattern opacity-20"></div>

      {/* Radial Glow Effect */}
      <div className="absolute inset-0 bg-gradient-radial from-blue-900/20 via-transparent to-transparent"></div>

      <div className="text-center relative z-10 px-4">
        <h1 className="text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-black tracking-tight leading-tight">
          {/* WELCOME - appears then fades out */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span
              className="text-white hover-glow animate-word-appear-fade"
              style={{
                animationDelay: "0s",
              }}
            >
              WELCOME
            </span>
          </div>

          {/* TO - appears then fades out */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span
              className="text-white hover-glow animate-word-appear-fade"
              style={{
                animationDelay: "0.6s",
              }}
            >
              TO
            </span>
          </div>

          {/* ChainOps AI - appears and lifts up, stays visible */}
          <div className="overflow-hidden">
            <span
              className="block opacity-0 animate-fadeInUp text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 animate-gradient relative"
              style={{
                animationDelay: "1.2s",
                animationFillMode: "forwards",
                textShadow: "0 0 80px rgba(59, 130, 246, 0.5)",
              }}
            >
              ChainOps AI
            </span>
          </div>
        </h1>
      </div>
    </div>
  );
};

export default IntroAnimation;
