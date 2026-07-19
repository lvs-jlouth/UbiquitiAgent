export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white px-4 py-4 text-center text-xs text-gray-500 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400 lg:px-6">
      <p>
        UniFi AI Operations Assistant &middot; &copy; {new Date().getFullYear()} &middot;
        Built for network operations teams
      </p>
    </footer>
  );
}

export default Footer;
