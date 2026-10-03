

document.addEventListener(
    "DOMContentLoaded",
    () => {
        const mainImage = document.querySelector(
            "[data-photo-album-image]"
        );

        const title = document.querySelector(
            "[data-photo-album-title]"
        );

        const folder = document.querySelector(
            "[data-photo-album-folder]"
        );

        const folderLink = document.querySelector(
            "[data-photo-album-folder-link]"
        );

        const description = document.querySelector(
            "[data-photo-album-description]"
        );

        const thumbnails = document.querySelectorAll(
            "[data-photo-album-thumbnail]"
        );

        if (
            !mainImage
            || !title
            || !folder
            || !folderLink
            || !description
            || !thumbnails.length
        ) {
            return;
        }

        const selectPhoto = (thumbnail) => {
            const photoUrl = thumbnail.dataset.photoUrl;
            const photoTitle = thumbnail.dataset.photoTitle;
            const folderName = thumbnail.dataset.photoFolderName;
            const folderUrl = thumbnail.dataset.photoFolderUrl;
            const photoDescription = (
                thumbnail.dataset.photoDescription || ""
            );

            mainImage.src = photoUrl;
            mainImage.alt = photoTitle;

            title.textContent = photoTitle;
            folder.textContent = folderName;
            folderLink.href = folderUrl;

            description.textContent = photoDescription;
            description.hidden = !photoDescription;

            thumbnails.forEach((item) => {
                const isSelected = item === thumbnail;

                item.setAttribute(
                    "aria-pressed",
                    isSelected ? "true" : "false"
                );

                item.classList.toggle(
                    "border-axcio-light",
                    isSelected
                );

                item.classList.toggle(
                    "border-transparent",
                    !isSelected
                );
            });

            thumbnail.scrollIntoView(
                {
                    behavior: "smooth",
                    block: "nearest",
                    inline: "nearest",
                }
            );
        };

        thumbnails.forEach((thumbnail) => {
            thumbnail.addEventListener(
                "click",
                () => {
                    selectPhoto(thumbnail);
                }
            );
        });
    }
);