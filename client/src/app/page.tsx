import Link from 'next/link';

const Page = () => {
  return (
    <div className="body flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-gray-200 to-white">
      <h1 className="text-3xl font-bold mb-8">Welcome</h1>
      <div className="flex flex-col space-y-4">
        <Link href="/signin" className="px-6 py-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition duration-300">
          Sign In
        </Link>
        <Link href="/signup" className="px-6 py-3 bg-green-600 text-white rounded-lg shadow-md hover:bg-green-700 transition duration-300">
          Sign Up
        </Link>
      </div>
    </div>
  );
};

export default Page;

