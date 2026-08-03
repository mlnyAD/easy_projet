

"use strict";

(function () {
    const DEFAULT_DURATION = 5000;
    const ANIMATION_DURATION = 200;
    const STACK_OFFSET_X = 10;
    const MAX_VISIBLE = 5;

    const container = document.querySelector(
        "[data-toast-container]"
    );

    if (!container) {
        return;
    }

    function getToasts() {
        return Array.from(
            container.querySelectorAll("[data-toast]")
        );
    }

    function refreshStack() {
        getToasts().forEach(function (toast, index) {
            const offset = index * STACK_OFFSET_X;

            toast.dataset.stackOffset = String(offset);

            if (toast.dataset.closing !== "true") {
                toast.style.transform =
                    `translateX(${offset}px)`;
            }
        });
    }

    function hideToast(toast) {
        if (!toast || toast.dataset.closing === "true") {
            return;
        }

        toast.dataset.closing = "true";

        const offset = Number.parseInt(
            toast.dataset.stackOffset || "0",
            10
        );

        toast.style.opacity = "0";
        toast.style.transform =
            `translateX(${offset + 16}px)`;

        const progressAnimation =
            toast._progressAnimation;

        if (progressAnimation) {
            progressAnimation.cancel();
        }

        window.setTimeout(function () {
            toast.remove();
            refreshStack();
        }, ANIMATION_DURATION);
    }

    function initializeToast(toast) {
        const closeButton = toast.querySelector(
            "[data-toast-close]"
        );

        const progress = toast.querySelector(
            "[data-toast-progress]"
        );

        const configuredDuration = Number.parseInt(
            toast.dataset.toastDuration || "",
            10
        );

        const duration = Number.isFinite(configuredDuration)
            ? configuredDuration
            : DEFAULT_DURATION;

        let timeoutId = null;
        let remainingDuration = duration;
        let startedAt = 0;

        let progressAnimation = null;

        if (progress) {
            progressAnimation = progress.animate(
                [
                    { transform: "scaleX(1)" },
                    { transform: "scaleX(0)" },
                ],
                {
                    duration: duration,
                    easing: "linear",
                    fill: "forwards",
                }
            );

            toast._progressAnimation =
                progressAnimation;
        }

        function startTimer() {
            startedAt = Date.now();

            timeoutId = window.setTimeout(
                function () {
                    hideToast(toast);
                },
                remainingDuration
            );
        }

        function pauseTimer() {
            if (timeoutId !== null) {
                window.clearTimeout(timeoutId);
                timeoutId = null;

                remainingDuration = Math.max(
                    0,
                    remainingDuration
                    - (Date.now() - startedAt)
                );
            }

            if (progressAnimation) {
                progressAnimation.pause();
            }
        }

        function resumeTimer() {
            if (
                timeoutId !== null
                || remainingDuration <= 0
                || toast.dataset.closing === "true"
            ) {
                return;
            }

            if (progressAnimation) {
                progressAnimation.play();
            }

            startTimer();
        }

        function closeImmediately() {
            if (timeoutId !== null) {
                window.clearTimeout(timeoutId);
                timeoutId = null;
            }

            hideToast(toast);
        }

        if (closeButton) {
            closeButton.addEventListener(
                "click",
                closeImmediately
            );
        }

        toast.addEventListener(
            "click",
            function (event) {
                if (
                    event.target.closest(
                        "[data-toast-close]"
                    )
                ) {
                    return;
                }

                closeImmediately();
            }
        );

        toast.addEventListener(
            "mouseenter",
            pauseTimer
        );

        toast.addEventListener(
            "mouseleave",
            resumeTimer
        );

        toast.addEventListener(
            "focusin",
            pauseTimer
        );

        toast.addEventListener(
            "focusout",
            resumeTimer
        );

        startTimer();
    }

    document.addEventListener(
        "DOMContentLoaded",
        function () {
            const toasts = getToasts();

            toasts
                .slice(MAX_VISIBLE)
                .forEach(function (toast) {
                    toast.remove();
                });

            const visibleToasts = getToasts();

            visibleToasts.forEach(
                initializeToast
            );

            refreshStack();

            window.requestAnimationFrame(
                function () {
                    visibleToasts.forEach(
                        function (toast) {
                            toast.style.opacity = "1";
                        }
                    );
                }
            );
        }
    );
})();